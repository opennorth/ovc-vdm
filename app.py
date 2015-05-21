# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, abort, request_started, jsonify, g, url_for, Response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource, inputs
from flask.ext.cache import Cache
from flask.ext.cors import CORS
from flask.ext.compress import Compress

from sqlalchemy.dialects.postgresql import array
from sqlalchemy.sql import func
from sqlalchemy import select,cast, desc, asc, inspect
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError
from werkzeug.wrappers import Request


from datetime import datetime
import time
from unidecode import unidecode
from itertools import ifilterfalse


import re
import os
import sys

from constants import OCDS_META
from serializations import CustomApi, generate_pdf, generate_csv, generate_xlsx
from utils import send_mail
import hashlib

#Initiate the APP

reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__, static_url_path='')
api = CustomApi(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
cors = CORS(app)
Compress(app)

#g.etag = datetime.now()


def before_request(sender, **extra):
    '''Called on request reception to log request before cache kicks in'''


    if request.path[0:5] == "/api/":
        daily = DailyStat(request)
        db.session.add(daily)
        db.session.commit()

request_started.connect(before_request, app)

@app.after_request
def after(response):
    ''' Add etag in response'''
    if hasattr(g, "etag") and g.etag != None:
        response.headers.add('etag', g.etag)
    return response

@app.errorhandler(404)
def internal_error(error):
    error_msg = {"msg": "Url %s does not exist" % request.url}
    resp = app.make_response(jsonify(error_msg))
    resp.status_code = 404
    
    return resp

@app.errorhandler(500)
def internal_error(error):
    '''Catch 500 errors and send custom message + alert email'''
    error_msg = {"msg": "Internal error - We are working on it!"}
    resp = app.make_response(jsonify(error_msg))
    resp.status_code = 500
    send_mail("Internal Error", "Internal generated for url %s" % request.url)
    return resp

@api.representation('application/pdf')
def output_pdf(data, code, headers=None):
    resp = app.make_response(generate_pdf(data))
    return resp


@api.representation('text/csv')
def output_csv(data, code, headers=None):
    resp = Response(generate_csv(data), mimetype='text/csv')
    #resp = app.make_response(generate_csv(data))
    return resp

@api.representation('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
def output_xlsx(data, code, headers=None):
    resp = app.make_response(generate_xlsx(data))
    return resp


def make_cache_key(*args, **kwargs):
    '''Make key for caching that integrates the args'''
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


from models import *



@app.route("/")
def root():
    return app.send_static_file('index.html')

class CustomResource(Resource):

    def dispatch_request(self, *args, **kwargs):
        '''Overload function to handle etag/If-None-Match behaviour'''

        last_update =  str(db.session.query(Source.last_retrieve).order_by("last_retrieve desc").first())
        g.etag = hashlib.sha1(str(last_update) + request.url).hexdigest()

        #Check if etag verified
        #print (str(request.headers.get('If-None-Match')),  g.etag) 
        if request.headers.get('If-None-Match') == g.etag :
            resp = app.make_response('')
            resp.status_code = 304
            return resp
        
        return super(CustomResource, self).dispatch_request(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(CustomResource, self).__init__(*args, **kwargs)

        self.supplier_joined = False
        self.buyer_joined = False

        self.default_limit = 50
        self.default_order_by = 'value'
        self.default_order_dir = 'asc'
        self.default_type = 'contract'

        self.accepted_parameters = [
            {"param": 'q', "type": str, "desc": "Free text search parameter, free text. e.g ?q=aménagement"},
            {"param": 'offset', "type": inputs.natural, "desc": "Pagination parameter. Positive integer number identifying the first record to return"},
            {"param": 'limit', "type": inputs.natural, "desc": "Pagination parameter. Positive integer number to limit the number of record to return, use with offet, e.g. ?limit=10&offset=20 will return records 20 to 30"},
            {"param": 'value_gt', "type": inputs.natural, "desc": "Filter on releases/contracts with value greater that the parameter. Positive integer number."},
            {"param": 'value_lt', "type": inputs.natural, "desc": "Filter on releases/contracts with value lesser that the parameter. Positive integer number."},
            {"param": 'date_gt', "type": inputs.date, "desc": "Filter on releases/contracts with date greater that the parameter. Positive integer number."},
            {"param": 'date_lt', "type": inputs.date, "desc": "Filter on releases/contracts with date lesser that the parameter. Positive integer number."},
            {"param": 'buyer', "type": str, "desc": "Filter by buyer, provide buyer slug to limit results to this buyer only."},
            {"param": 'activity', "type": str, "desc": "Filter by activity, provide activity to limit results to this activity only."}, 
            {"param": 'supplier', "type": str, "desc": "Filter by supplier, provide supplier slug to limit results to this supplier only."},
            {"param": 'order_by', "type": str, "desc": "Criteria used to order results. See accepted_order_by for acceted values for each end point"}, 
            {"param": 'order_dir', "type": str, "desc": "Direction for the order criteria. Value 'desc' or 'asc'"},
            {"param": 'type', "type": str, "desc": "Type of contract. Accepted values: 'contract' or 'subvention'"},
            {"param": 'supplier_size', "type": str, "desc": "Filter by the size of supplier. Accepted values: 1 (smaller),2 and 3 (larger)"},
            {"param": 'procuring_entity', "type": str, "desc": "Filter by procuring entity, provide procuring entity to limit results to this procuring entity only."},                 

        ]

        self.accepted_order_by = ['value', 'buyer', 'supplier', 'id', 'date', None]
        self.accepted_type = ['subvention', 'contract', None]


    def parse_arg(self):
        parser = reqparse.RequestParser()        
        for parameter in self.accepted_parameters:
            parser.add_argument(parameter["param"], type=parameter["type"], location='args')

        args = parser.parse_args(strict=True)

        if 'order_by' in args and args['order_by'] not in self.accepted_order_by:
            abort(400, message='Order by value must be %s' % self.accepted_order_by)

        if 'order_dir' in args and args['order_dir'] not in ['asc', 'desc', None]:
            abort(400, message='order_dir value must be "asc" or "desc"')

        return args

    def sort_request(self, query, args):

        if 'order_by' in args and args['order_by'] == "buyer":
            args['order_by'] = "buyers.slug"

        if  'order_by' in args and args['order_by'] == "supplier":
            args['order_by'] = "suppliers.slug"

        sort_attr = self.default_order_by
        if ('order_by' in args and args['order_by'] != None):
            sort_attr = args['order_by']
        
        sorter = self.default_order_dir
        if 'order_dir' in args :
            if args['order_dir'] == 'desc': 
                sorter = 'desc'
            elif args['order_dir'] == 'asc':
                sorter = 'asc'

        return query.order_by("%s %s" % (sort_attr, sorter) )

    def highlight_request (self, query, args):

        highlighted_fields = [(Release.description, 'h_description'), 
                                (Supplier.name, 'h_supplier_name'),
                                (Buyer.name, 'h_buyer_name'),
                                (Release.dossier, 'h_dossier'),
                                (Release.decision, 'h_decision')
        ]

        if 'q' in args and args['q'] != None and 'highlight' in args and args['highlight'] == True: 
            for (field, label) in highlighted_fields:
                query = query.add_column(func.ts_headline(app.config["FTS_LANG"], 
                           field, 
                           func.plainto_tsquery(app.config["FTS_LANG"], args['q']),
                           'HighlightAll=TRUE, StartSel="%s", StopSel = "%s"' % (app.config["START_HIGHLIGHT"], app.config["END_HIGHLIGHT"]))
                            .label(label))   
                            
        return query     

    def highlight_result(self, result, args):

        if 'q' in args and args['q'] != None and 'highlight' in args and args['highlight'] == True: 
            result.json["awards"][0]["items"][0]["description"] = result.h_description
            result.json["awards"][0]["suppliers"][0]["name"] = result.h_supplier_name
            result.json["buyer"]["name"] = result.h_buyer_name
            result.json["awards"][0]["id"] = result.h_dossier
            result.json["awards"][0]["items"][0]["id"] = result.h_decision

        return result

    def filter_request(self, query, args):

        #By default we filter contracts
        con_type = args['type'] if ('type' in args and args['type'] != None) else self.default_type
        query = query.filter(Release.type == con_type)

        if 'q' in args and args['q'] != None:
            search = unidecode(unicode(args['q'])).replace(" ", "&")
            query = query.filter(func.to_tsvector(app.config["FTS_LANG"], Release.concat).match(search, postgresql_regconfig=app.config["FTS_LANG"]))
        
        if 'value_gt' in args and args['value_gt'] != None:
            query = query.filter(Release.value >= args['value_gt'])


        if 'value_lt' in args and args['value_lt'] != None:
            query = query.filter(Release.value <= args['value_lt'])

        if 'date_gt' in args and args['date_gt'] != None:
            query = query.filter(Release.date >= args['date_gt'])


        if 'date_lt' in args and args['date_lt'] != None:
            query = query.filter(Release.date <= args['date_lt'])

        if 'buyer' in args and args['buyer'] != None:
            if self.buyer_joined == False:
                query = query.join(Buyer)
                self.buyer_joined = True

            query = query.filter(array(args['buyer'].split(';')).any(Buyer.slug))

        if 'activity' in args and args['activity'] != None:
            query = query.filter(Release.activities.overlap(args['activity'].split(';')))

        if 'procuring_entity' in args and args['procuring_entity'] != None:
            query = query.filter(array(args['procuring_entity'].split(';')).any(Release.procuring_entity_slug))

        if ('supplier' in args and args['supplier'] != None) or ('supplier_size' in args and args['supplier_size'] != None):
        
            if self.supplier_joined == False:
                query = query.join(Supplier)
                self.supplier_joined = True


            if ('supplier' in args and args['supplier'] != None):
                query = query.filter(array(args['supplier'].split(';')).any(Supplier.slug))

            if ('supplier_size' in args and args['supplier_size'] != None):
                integered = [ int(item) for item in args['supplier_size'].split(';')]
                query = query.filter(array(integered).any(Supplier.size))

        return query          


    def offset_limit(self, query, args):
        (offset,limit) = (0,self.default_limit)

        if 'offset' in args and args['offset'] != None:
            offset = args['offset']
        if 'limit' in args and args['limit'] != None:
            limit = args['limit']
        
        return (query[offset:offset+limit], offset, limit)



class ListReleases(CustomResource):
    '''Provide list releases following the Open Contracting format based on filters provided'''

    def __init__(self, *args, **kwargs):
        super(ListReleases, self).__init__(*args, **kwargs)

        self.default_order_by = 'date'
        self.default_order_dir = 'desc'

        self.accepted_parameters.append({"param": 'highlight', "type": bool, "desc": "Highlight search results. If set to 'True', add a <em> on search terms provided in parameter 'q'"})
        self.accepted_parameters.append({"param": 'format', "type": str, "desc": "Select output format. Accepter values: 'json' (default), 'ocds': static OCDS file, 'pdf': PDF file, 'csv': CSV file, 'xlsx': MS Excel"})

                

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):

        output = dict()

        try:
        
            args = self.parse_arg()

            self.supplier_joined = True
            self.buyer_joined = True
            
            releases = db.session.query(Release.json).join(Buyer).join(Supplier)
            releases = self.highlight_request(releases, args)



            releases_sum = db.session.query(
                func.sum(Release.value).label('total_value'), 
                func.max(Release.value).label('max_value'), 
                func.min(Release.value).label('min_value'))
          
            releases = self.filter_request(releases, args)
            

            release_count = releases.count()
            #Sort records
            releases = self.sort_request(releases, args)

            

            #Limit and offset
            (releases, offset, limit) = self.offset_limit(releases, args)

            self.supplier_joined = False
            self.buyer_joined = False
            releases_sum = self.filter_request(releases_sum, args)

            #Generate output structure
            

                
            output["meta"] = {
                "count": release_count,
                "pagination" : {"offset" : offset, "limit":  limit}
            }

            output["meta"].update(releases_sum.one()._asdict())

            output.update(OCDS_META)
            output["uri"] = request.url
            output["publishedDate"] = datetime.now().isoformat()

            #output["releases"] = [r.json for r in releases]

            output["releases"] = [] 
            for r in releases:
                r = self.highlight_result(r, args)
                output["releases"].append(r.json)


        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message="Database error %s" % e) 

        return output

api.add_resource(ListReleases, '/api/releases', '/api/releases.csv', '/api/releases.xlsx', '/api/releases.pdf', '/api/releases.json')

class ReleasesBySupplier(CustomResource):
    '''Group releases by  supplier and provide the number of contracts and the total 
    value of contracts by supplier'''

    def __init__(self, *args, **kwargs):
        super(ReleasesBySupplier, self).__init__(*args, **kwargs)

        self.supplier_joined = True
        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'supplier_size', 'supplier_slug', None]


    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()



        releases = db.session.query(
            func.sum(Release.value).label('total_value'), 
            func.count(Release.value).label('count'),      
            Supplier.name.label('supplier'), 
            func.min(Supplier.slug).label('supplier_slug'),
            func.min(Supplier.size).label('supplier_size'))

        releases = self.filter_request(releases, args)
        releases = releases.filter(Supplier.id == Release.supplier_id)
        releases = releases.group_by(Supplier.name)
        releases = self.sort_request(releases, args)
        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)

        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        output["releases"] = [r._asdict() for r in releases] 

        return output 
api.add_resource(ReleasesBySupplier, '/api/releases/by_supplier')


class ReleasesByBuyer(CustomResource):
    '''Group releases by buyer. Provide the number of contract and total
    value for each buyer'''

    def __init__(self, *args, **kwargs):
        super(ReleasesByBuyer, self).__init__(*args, **kwargs)

        self.buyer_joined = True
        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'buyer_slug', None]

    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            func.count(Release.value).label('count'),
            func.min(Release.activities).label('activities'), 
            func.sum(Release.value).label('total_value'), 
            Buyer.name.label('buyer'),            
            func.min(Buyer.slug).label('buyer_slug'))

        releases = self.filter_request(releases, args)
        releases = releases.filter(Buyer.id == Release.buyer_id)
        releases = releases.group_by(Buyer.name)
        releases = self.sort_request(releases, args)
        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)

        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        output["releases"] = [r._asdict() for r in releases] 

        return output 
api.add_resource(ReleasesByBuyer, '/api/releases/by_buyer')


class ReleasesByProcuringEntity(CustomResource):
    '''Group releases by procuring entity. Provide the number of contract and total
    value for each procuring entity'''


    def __init__(self, *args, **kwargs):
        super(ReleasesByProcuringEntity, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'procuring_entity', None]

    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            Release.procuring_entity.label('procuring_entity'),
            func.min(Release.procuring_entity_slug).label('procuring_entity_slug'),
            func.sum(Release.value).label('total_value'), 
            func.count(Release.value).label('count'))

        releases = self.filter_request(releases, args)
        releases = releases.group_by(Release.procuring_entity)
        releases = self.sort_request(releases, args)
        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)

        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        output["releases"] = [r._asdict() for r in releases] 

        return output 
api.add_resource(ReleasesByProcuringEntity, '/api/releases/by_procuring_entity')


class ReleasesByValueRange(CustomResource):
    '''Group releases by buckets of value. Parameter 'bucket' is mandatory for this endpoint.
    Provide the start value, end value and number of intervals, the endpoint returns the number
    of contracts and total value for each segment of value'''

    def __init__(self, *args, **kwargs):
        super(ReleasesByValueRange, self).__init__(*args, **kwargs)

        self.default_limit = 5000
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'segment', None]
        self.width_bucket = (0, 10000000, 19)

        self.accepted_parameters.append({"param": 'bucket', "type": str, "desc": "Parameters of the value bucket for the by_value endpoint. 3 coma-separated positive integer: first, minimum value; second, maximum value, third, number of intervals. E.g by_value?bucket=0,10000000,49"})

    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        if args["bucket"] != None:
            self.width_bucket = args["bucket"].split(',')
  
        releases = db.session.query(
            width_bucket(Release.value, self.width_bucket[0], self.width_bucket[1], self.width_bucket[2]).label('segment'),
            func.sum(Release.value).label('total_value'),
            func.count(Release.value).label('count'))
        releases = self.filter_request(releases, args)
        releases = releases.group_by('1')
        releases = self.sort_request(releases, args)
        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)

        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        output["releases"] = [r._asdict() for r in releases] 

        return output 
api.add_resource(ReleasesByValueRange, '/api/releases/by_value')


class ReleasesByMonth(CustomResource):
    '''Group releases by month-year. Provide the number of contract and total
    value for each month-year where some contracts are available'''    

    def __init__(self, *args, **kwargs):
        super(ReleasesByMonth, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = '1'
        self.default_order_dir = 'asc'
        self.accepted_order_by = ['total_value', 'count', 'month', None]


    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            func.substring(cast(Release.date, db.String), 0,8).label('month'), 
            func.count(Release.value).label('count'), 
            func.sum(Release.value).label('total_value'))

        releases = self.filter_request(releases, args)
        releases = releases.group_by('1')
        releases = self.sort_request(releases, args)
        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)

        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        output["releases"] = [r._asdict() for r in releases] 

        return output 
api.add_resource(ReleasesByMonth, '/api/releases/by_month')

class ReleasesByActivity(CustomResource):
    '''Group releases by activity. Provide the number of contracts and total value
    for each activity available. On the primary (first in the list) activity is considered'''

    def __init__(self, *args, **kwargs):
        super(ReleasesByActivity, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'activity', None]

    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            Release.activities[1].label('activity'), 
            func.sum(Release.value).label('total_value'), 
            func.count(Release.value).label('count'))      
        releases = self.filter_request(releases, args)
        releases = releases.group_by('1')
        releases = self.sort_request(releases, args)

        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)

        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        output["releases"] = [r._asdict() for r in releases] 

        return output 
api.add_resource(ReleasesByActivity, '/api/releases/by_activity')

class ReleasesByMonthActivity(CustomResource):
    '''Group releases by month-year and then by activity. Provide the number of contract and total
    value for each month-year/activity pairs where some contracts are available'''    

    def __init__(self, *args, **kwargs):
        super(ReleasesByMonthActivity, self).__init__(*args, **kwargs)

        self.default_limit = 1000
        self.default_order_by = '1'
        self.default_order_dir = 'asc'
        self.accepted_order_by = ['total_value', 'count', 'month', None]

        self.accepted_parameters.append({"param": 'aggregate', "type": str, "desc": "For by_month_activity, aggregate acitivities after top N results"})



    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            func.substring(cast(Release.date, db.String), 0,8).label('month'), 
            Release.activities[1].label('activity'), 
            func.count(Release.value).label('count'), 
            func.sum(Release.value).label('total_value'))

        releases = self.filter_request(releases, args)
        releases = releases.group_by('month', 'activity')
        releases = self.sort_request(releases, args)
        
        release_count = releases.count()

        (releases, offset, limit) = self.offset_limit(releases, args)



        #Generate output structure
        output = dict()
            
        output["meta"] = {
            "count": release_count,
            "pagination" : {"offset" : offset, "limit":  limit}
        }

        months_dict = {}

        for release in releases:
            r = release._asdict()
            current_month = r["month"]
            del r["month"]

            if current_month not in months_dict:
                months_dict[current_month] = []


            months_dict[current_month].append(r)

        output["releases"] = [{"month" : month, "activities": activities} for month,activities in months_dict.iteritems()] 

                
        if 'aggregate' in args and (args['aggregate'] == "value" or args['aggregate'] == "count"):
            top = []
            activities = db.session.query(
                Release.activities[1].label('activity'), 
                func.sum(Release.value).label('total_value'), 
                func.count(Release.value).label('count'))

            activities = self.filter_request(activities, args)
            activities = activities.filter(Release.activities[1] != "Autre")         
            activities = activities.group_by('activity')

            if args['aggregate'] == "value":
                activities = activities.order_by("total_value desc")
            else :
                activities = activities.order_by("count desc")

            activities = activities[0:app.config["AGG_ACTIVITIES"]]

            top = [a._asdict()['activity'] for a in activities]

            print top
        
            for m in output["releases"]:

                count = 0
                total_value = 0
                for  i, a in reversed(list(enumerate(m["activities"]))):

                    if a["activity"] not in top:
                        count += a["count"]
                        total_value += a["total_value"]
                        del m["activities"][i]
                        
                if count > 0 and total_value > 0:

                    autre = {"activity": "Autre", "count": count,"total_value": total_value}
                    m["activities"].append(autre)



        return output 
api.add_resource(ReleasesByMonthActivity, '/api/releases/by_month_activity')



class IndividualRelease(CustomResource):
    '''Provide OCDS formatted output for an individual release given its OCID'''

    def __init__(self, *args, **kwargs):
        super(IndividualRelease, self).__init__(*args, **kwargs)


        self.supplier_joined = True
        self.buyer_joined = True

        self.default_order_by = None
        self.default_order_dir = None
        self.accepted_order_by = None
        self.accepted_type = None

        self.accepted_parameters = [
            {"param": 'q', "type": str},
            {"param": 'highlight', "type": bool},
        ]



    @cache.cached(timeout=app.config["CACHE_DURATION"], key_prefix=make_cache_key)
    def get(self,ocid):

        args = self.parse_arg()
        try:


            my_release = db.session.query(Release.json).join(Buyer).join(Supplier)
            my_release = my_release.filter(Release.ocid==ocid)
            my_release = self.highlight_request(my_release, args)

            r = my_release.one()
            r = self.highlight_result(r, args)
            return r.json

        except NoResultFound:
            abort(404, message="Release {} does not exist".format(ocid)) 

api.add_resource(IndividualRelease, '/api/release/<string:ocid>')


class BuyerSlugs(CustomResource):
    @cache.cached(timeout=app.config["CACHE_DURATION"])
    def get(self):
        buyers = db.session.query(Buyer.name, Buyer.slug)
        output = {"buyers": [b._asdict() for b in buyers]}

        return output
        
    
api.add_resource(BuyerSlugs, '/api/helpers/buyer_slugs')


class SupplierSlugs(CustomResource):
    @cache.cached(timeout=app.config["CACHE_DURATION"])
    def get(self):
        suppliers = db.session.query(Supplier.name, Supplier.slug)

        output = {"suppliers" : [s._asdict() for s in suppliers]}

        return output
        
api.add_resource(SupplierSlugs, '/api/helpers/supplier_slugs')

class ActivityList(CustomResource):
    @cache.cached(timeout=app.config["CACHE_DURATION"])
    def get(self):
        activity_dict = app.config["ACTIVITY_COLOR_CODE"]

        activities = db.session.query(
            Release.activities[1].label('activity'), 
            func.sum(Release.value).label('total_value'))

        activities = activities.group_by('activity')
        activities = activities.order_by("total_value desc")

        activities = activities[0:app.config["AGG_ACTIVITIES"]]

        top = [a._asdict()['activity'] for a in activities]
        output = {"activities" : []}

        for key,value in activity_dict.iteritems():
            agg = True
            if key in top:
                agg = False

            output["activities"].append({"name": key, "color_code": value, "aggregate": agg} )

        return output
        
api.add_resource(ActivityList, '/api/helpers/activity_list')

class TriggerError(Resource):
    def get(self):
        raise NoResultFound
    
api.add_resource(TriggerError, '/api/trigger_500')

#Define routes for API
class ApiRoot(CustomResource):
    '''Root API listing available ressource, and general informations about the 
    data available in the system'''
    @cache.cached(timeout=app.config["CACHE_DURATION"])
    def get(self):

        resource_list = ["ListReleases", "ReleasesBySupplier", "ReleasesByBuyer", 
        "ReleasesByProcuringEntity", "ReleasesByValueRange", "ReleasesByMonth", "ReleasesByActivity"]

        def has_no_empty_params(rule):
            defaults = rule.defaults if rule.defaults is not None else ()
            arguments = rule.arguments if rule.arguments is not None else ()
            return len(defaults) >= len(arguments)

        url_dict = {}
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint)  
                url_dict[rule.endpoint] = url


        releases_dict = {}
        releases_dict["endpoints"] = []
        parameters_dict = {}

        for resource in resource_list:
            resource_dict = {}
            resource_dict["url"] = url_dict[resource.lower()]

            introspection = eval(resource)()

            
            resource_dict["accepted_parameters"] = [param["param"] for param in introspection.accepted_parameters]

            for param in introspection.accepted_parameters:
                if "desc" in param and param["param"] not in parameters_dict:
                    parameters_dict[param["param"]] = param["desc"]


            resource_dict["accepted_order_by"] = [order for order in introspection.accepted_order_by]

            if introspection.__doc__ != None:
                resource_dict["description"] = introspection.__doc__

            releases_dict["endpoints"].append(resource_dict)

        releases_dict["parameters_description"] = parameters_dict
        releases_dict["sources"] = [source.url for source in Source.query.all()]
        releases_dict["last_update"] = (db.session.query(Source.last_retrieve).order_by("last_retrieve desc").first()[0]).strftime("%Y-%m-%dT%H:%M:%S")
        releases_dict["releases_count"] = db.session.query(Release).count()
        releases_dict["releases_value"] = db.session.query(func.sum(Release.value).label('sum')).scalar()
        releases_dict["supplier_count"] = db.session.query(Supplier).count()
        releases_dict["buyer_count"] = db.session.query(Buyer).count()
        releases_dict["buyer_range"] = app.config["SUPPLIER_SIZE"]


        return releases_dict

api.add_resource(ApiRoot, '/api/')



if __name__ == '__main__':
    app.run()