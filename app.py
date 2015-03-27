
from flask import Flask, render_template, request, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource, inputs
from flask.ext.cache import Cache
from flask.ext.cors import CORS

from sqlalchemy.dialects.postgresql import array
from sqlalchemy.sql import func
from sqlalchemy import select,cast, desc, asc
from sqlalchemy.orm.exc import NoResultFound

from datetime import datetime
#from utils import  unaccent
from unidecode import unidecode

import re
import os
import sys

from constants import OCDS_META
from serializations import CustomApi, generate_pdf, generate_csv, generate_xlsx

#Initiate the APP

reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
api = CustomApi(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
cors = CORS(app)

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
def index():
    return render_template('index.html')



class ListReleases(Resource):

    def __init__(self, *args, **kwargs):
        super(ListReleases, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'value'
        self.default_order_dir = 'asc'
        self.default_type = 'contract'

        self.accepted_parameters = [
            {"param": 'q', "type": str},
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

        self.accepted_order_by = ['value', 'buyer', 'id', 'date', None]
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

        sort_attr = self.default_order_by
        if ('order_by' in args and args['order_by'] != None):
            sort_attr = args['order_by']
        
        sorter = self.default_order_dir
        if ('order_dir' in args and 'order_dir' in args and args['order_dir'] == 'desc'):
            sorter = 'desc'

        return query.order_by("%s %s" % (sort_attr, sorter) )

    def filter_request(self, query, args):


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
            query = query.join(Buyer).filter(array(args['buyer'].split(',')).any(Buyer.slug))

        if 'activity' in args and args['activity'] != None:
            query = query.filter(Release.activities.overlap(args['activity'].split(',')))

        if 'procuring_entity' in args and args['procuring_entity'] != None:
            query = query.filter(array(args['procuring_entity'].split(',')).any(Release.procuring_entity_slug))

        if ('supplier' in args and args['supplier'] != None) or ('supplier_size' in args and args['supplier_size'] != None):
            query = query.join(Supplier)

            if ('supplier' in args and args['supplier'] != None):
                query = query.filter(array(args['supplier'].split(',')).any(Supplier.slug))

            if ('supplier_size' in args and args['supplier_size'] != None):
                integered = [ int(item) for item in args['supplier_size'].split(',')]
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


        releases = db.session.query(Release)
        releases_sum = db.session.query(func.sum(Release.value).label('total_value'), func.max(Release.value).label('max_value'), func.min(Release.value).label('min_value'))
      
        releases = self.filter_request(releases, args)
        releases_sum = self.filter_request(releases_sum, args)

        #Sort records
        releases = self.sort_request(releases, args)

        release_count = releases.count()

        #Limit and offset
        (releases, offset, limit) = self.offset_limit(releases, args)

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

        output["releases"] = [r.json for r in releases] 

        return output

api.add_resource(ListReleases, '/api/releases')

class ReleasesBySupplier(ListReleases):

    def __init__(self, *args, **kwargs):
        super(ReleasesBySupplier, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'supplier_size', 'supplier_slug', None]

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()



        releases = db.session.query(
            Supplier.name.label('supplier'), 
            func.min(Supplier.slug).label('supplier_slug'),
            func.min(Supplier.size).label('supplier_size'),
            func.sum(Release.value).label('total_value'), 
            func.count(Release.value).label('count'))      
        releases = self.filter_request(releases, args)
        releases = releases.filter(Supplier.id == Release.supplier_id)
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
api.add_resource(ReleasesBySupplier, '/api/releases/by_supplier')


class ReleasesByBuyer(ListReleases):

    def __init__(self, *args, **kwargs):
        super(ReleasesByBuyer, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'
        self.accepted_order_by = ['total_value', 'count', 'buyer_slug', None]

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            Buyer.name.label('buyer'),
            func.min(Release.activities).label('activities'), 
            func.min(Buyer.slug).label('buyer_slug'), 
            func.sum(Release.value).label('total_value'), 
            func.count(Release.value).label('count'))
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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
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


    @cache.cached(timeout=5000, key_prefix=make_cache_key)
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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
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


class TreeMap(ListReleases):

    def __init__(self, *args, **kwargs):
        super(TreeMap, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'total_value'
        self.default_order_dir = 'desc'

        self.accepted_parameters = [
            {"param": 'parent', "type": str}, 
            {"param": 'child', "type": str}, 
            {"param": 'limit', "type": inputs.natural},
            {"param": 'date_gt', "type": inputs.date},
            {"param": 'date_lt', "type": inputs.date},
            {"param": 'buyer', "type": str},
            {"param": 'activity', "type": str}, 
            {"param": 'supplier', "type": str},            
            {"param": 'type', "type": str},    
        ]

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        if args["parent"] == "activity":
            releases = db.session.query(Release.activities[1].label(args["parent"]), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))            
        elif args["parent"] == "buyer":
            releases = db.session.query(Buyer.name.label('buyer'), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
            releases = releases.filter(Buyer.id == Release.buyer_id)
        elif args["parent"] == "size":
            releases = db.session.query(Supplier.size.label('size'), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
            releases = releases.filter(Supplier.id == Release.supplier_id)

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


        for item in output["releases"]:
            if args["child"] == "buyer":
                children = db.session.query(Buyer.name.label('buyer'), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
                children = children.filter(Buyer.id == Release.buyer_id)                
            elif args["child"] == "supplier":
                children = db.session.query(Supplier.name.label('supplier'), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
                children = children.filter(Supplier.id == Release.supplier_id)  
            else:
                children = db.session.query(getattr(Release, args["child"]).label(args["child"]), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))

            if args["parent"] == "activity":
                children = children.filter(Release.activities[1] == item[args['parent']])
            elif args["parent"] == "buyer":
                children = children.filter(Buyer.name == item[args['parent']]) 
            elif args["parent"] == "size":
                children = children.filter(Supplier.size == item[args['parent']])  

            children = self.filter_request(children, args)
            children = children.group_by('1')
            children = children.order_by('total_value desc')

            (children, offset, limit) = self.offset_limit(children, args)

            item["children"] = []
            for child in children:
                item["children"].append(child._asdict())

        return output 
api.add_resource(TreeMap, '/api/treemap')

class IndividualRelease(Resource):
    @cache.cached(timeout=5000)
    def get(self,ocid):
        try:
            my_release = Release.query.filter_by(ocid=ocid).one()
            return my_release.json
        except NoResultFound:
            abort(404, message="Release {} does not exist".format(ocid)) 

api.add_resource(IndividualRelease, '/api/release/<string:ocid>')


#Define routes for API
class ApiRoot(Resource):
    def get(self):
        accept_header = request.headers.get('Accept')
        request.headers.get('Accept')

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