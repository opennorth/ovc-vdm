
from flask import Flask, render_template, request, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource, inputs
from flask.ext.cache import Cache
from flask.ext.cors import CORS

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

        buyer_dict = {}
        buyer_dict["url"] = '/buyers'
        buyer_dict["count"] = buyers 

        output = {}
        output["releases"] = releases_dict
        output["buyer"] = buyer_dict 
 
        return output
api.add_resource(ApiRoot, '/api/')



class ListReleases(Resource):

    def __init__(self, *args, **kwargs):
        super(ListReleases, self).__init__(*args, **kwargs)

        self.default_limit = 50
        self.default_order_by = 'value'
        self.default_order_dir = 'asc'

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
            {"param": 'format', "type": str},
        ]

        self.accepted_order_by = ['value', 'buyer', 'id', 'date', None]


    def parse_arg(self):
        parser = reqparse.RequestParser()        
        for parameter in self.accepted_parameters:
            parser.add_argument(parameter["param"], type=parameter["type"], location='args')

        args = parser.parse_args(strict=True)

        if args['order_by'] not in self.accepted_order_by:
            abort(400, message='Order by value must be %s' % accepted_order_by)

        if args['order_dir'] not in ['asc', 'desc', None]:
            abort(400, message='order_dir value must be "asc" or "desc"')

        return args

    def sort_request(self, query, args):

        sort_attr = self.default_order_by
        if (args['order_by'] != None):
            sort_attr = args['order_by']
        
        sorter = self.default_order_dir
        if ('order_dir' in args and args['order_dir'] == 'desc'):
            sorter = 'desc'

        return query.order_by("%s %s" % (sort_attr, sorter) )

    def filter_request(self, query, args):
        if args['q'] != None:
            search = unidecode(unicode(args['q'])).replace(" ", "&")
            query = query.filter(func.to_tsvector('fr', Release.concat).match(search))
        
        if args['value_gt'] != None:
            query = query.filter(Release.value >= args['value_gt'])


        if args['value_lt'] != None:
            query = query.filter(Release.value <= args['value_lt'])

        if args['date_gt'] != None:
            query = query.filter(Release.date >= args['date_gt'])


        if args['date_lt'] != None:
            query = query.filter(Release.date <= args['date_lt'])

        if args['buyer'] != None:
            query = query.join(Buyer).filter(Buyer.slug == args['buyer'])

        if args['activity'] != None:
            #select_stmt = select([Release]).where(Release.activities.any(args['activity']))
            #query = query.select_entity_from(select_stmt)

            query = query.filter(Release.activities.any(args['activity']))

        if args['supplier'] != None:
            query = query.filter(Release.supplier_slug == args['supplier'])

        return query          


    def offset_limit(self, query, args):
        (offset,limit) = (0,self.default_limit)

        if args['offset'] != None:
            offset = args['offset']
        if args['limit'] != None:
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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(Release.supplier.label('supplier'), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))      
        releases = self.filter_request(releases, args)
        releases = releases.group_by(Release.supplier)
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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
            Buyer.name.label('buyer'),
            func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
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
        self.default_order_by = '1'
        self.default_order_dir = 'asc'

        self.width_bucket = (0, 10000000, 19)

        self.accepted_parameters.append({"param": 'bucket', "type": str})

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        if args["bucket"] != None:
            self.width_bucket = args["bucket"].split(',')
  
        releases = db.session.query(
        width_bucket(Release.value, self.width_bucket[0], self.width_bucket[1], self.width_bucket[2]).label('segment'),
        func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
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


    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(
        func.substring(cast(Release.date, db.String), 0,8).label('month'), func.count(Release.value).label('count'), func.sum(Release.value).label('total_value'))

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

    @cache.cached(timeout=5000, key_prefix=make_cache_key)
    def get(self):
        args = self.parse_arg()

        releases = db.session.query(Release.activities[1].label('activity'), func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))      
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

class IndividualRelease(Resource):
    @cache.cached(timeout=5000)
    def get(self,ocid):
        try:
            my_release = Release.query.filter_by(ocid=ocid).one()
            return my_release.json
        except NoResultFound:
            abort(404, message="Release {} does not exist".format(ocid)) 

api.add_resource(IndividualRelease, '/api/release/<string:ocid>')

if __name__ == '__main__':
    app.run()


