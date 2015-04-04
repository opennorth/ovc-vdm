# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, abort, request_started, jsonify, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource, inputs
from flask.ext.cache import Cache
from flask.ext.cors import CORS
from flask.ext.compress import Compress

from sqlalchemy.dialects.postgresql import array
from sqlalchemy.sql import func
from sqlalchemy import select,cast, desc, asc, inspect
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from werkzeug.wrappers import Request


from datetime import datetime
from unidecode import unidecode


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
stats_log = open(app.config["STATS_LOG"],'a')
#g.etag = datetime.now()


def before_request(sender, **extra):

    #Je note
    req = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S") , "path": request.path, "args": [(key,value) for (key,value) in request.args.items()], "referrer" : request.referrer }    
    stats_log.write(str(req) + '\n')   
    stats_log.flush() 


request_started.connect(before_request, app)




@app.after_request
def after(response):
    if g.etag != None:
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
    resp = app.make_response(generate_csv(data))
    return resp

@api.representation('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
def output_xlsx(data, code, headers=None):
    resp = app.make_response(generate_xlsx(data))
    return resp


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


from models import *


#Define routes for HTML content
@app.route("/")
def root():
    return app.send_static_file('index.html')



class ListReleases(Resource):

    def dispatch_request(self, *args, **kwargs):

        #Generate etag
        last_update =  str(db.session.query(Source.last_retrieve).order_by("last_retrieve desc").first())
        g.etag = hashlib.sha1(str(last_update) + request.url).hexdigest()

        #Check if etag verified
        if request.headers.get('If-None-Match') == g.etag:
            resp = app.make_response('')
            resp.status_code = 304
            return resp
        
        return super(ListReleases, self).dispatch_request(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ListReleases, self).__init__(*args, **kwargs)

        self.supplier_joined = False
        self.buyer_joined = False

        self.default_limit = 50
        self.default_order_by = 'value'
        self.default_order_dir = 'asc'
        self.default_type = 'contract'

        self.accepted_parameters = [
            {"param": 'q', "type": str},
            {"param": 'highlight', "type": bool},
            {"param": 'offset', "type": inputs.natural},
            {"param": 'limit', "type": inputs.natural},
            {"param": 'value_gt', "type": inputs.natural},
            {"param": 'value_lt', "type": inputs.natural},
            {"param": 'date_gt', "type": inputs.date},
            {"param": 'date_lt', "type": inputs.date},
            {"param": 'buyer', "type": str},
            {"param": 'activity', "type": str}, 
            {"param": 'supplier', "type": str},
            {"param": 'order_by', "type": str}, 
            {"param": 'order_dir', "type": str},
            {"param": 'type', "type": str},
            {"param": 'supplier_size', "type": str},
            {"param": 'procuring_entity', "type": str},                 
            {"param": 'format', "type": str},
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
        if ('order_dir' in args and 'order_dir' in args and args['order_dir'] == 'desc'):
            sorter = 'desc'

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
                query = query.add_column(func.ts_headline('french', 
                           field, 
                           func.plainto_tsquery(args['q']),
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
            query = query.filter(func.to_tsvector('french', Release.concat).match(search))
        
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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        
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
        output = dict()

            
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


        return output

api.add_resource(ListReleases, '/api/releases')

class ReleasesBySupplier(ListReleases):

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


class ReleasesByBuyer(ListReleases):

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


class ReleasesByProcuringEntity(ListReleases):

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
            func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
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


class ReleasesByValueRange(ListReleases):

    def __init__(self, *args, **kwargs):
        super(ReleasesByValueRange, self).__init__(*args, **kwargs)

        self.default_limit = 5000
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'segment', None]
        self.width_bucket = (0, 10000000, 19)

        self.accepted_parameters.append({"param": 'bucket', "type": str})

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


class ReleasesByMonth(ListReleases):

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

class ReleasesByActivity(ListReleases):

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


class IndividualRelease(ListReleases):

    def __init__(self, *args, **kwargs):
        super(ListReleases, self).__init__(*args, **kwargs)


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


class TriggerError(Resource):
    def get(self):
        raise NoResultFound
    
api.add_resource(TriggerError, '/api/trigger_500')

#Define routes for API
class ApiRoot(ListReleases):
    def get(self):


        releases = db.session.query(Release).count()
        releases_sum = db.session.query(func.sum(Release.value).label('sum')).scalar()
        buyers = db.session.query(Buyer).count()

        releases_dict = {}
        releases_dict["url"] = '/releases'
        releases_dict["count"] = releases
        releases_dict["value"] = releases_sum

        '''
        list_releases = ListReleases()
        print [item["param"] for item in list_releases.accepted_parameters]
        releases_dict["params"] = [item["param"] for item in list_releases.accepted_parameters]

        print api.__dict__
        '''

        output = {}
        output["releases"] = releases_dict
 
        return output
api.add_resource(ApiRoot, '/api/')

if __name__ == '__main__':
    app.run()