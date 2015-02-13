from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource
from sqlalchemy.orm.exc import *
from sqlalchemy.sql import func
from sqlalchemy import select,cast
import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
api = Api(app)

#use env variable to get what type of environment we have
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)

from models import *

class Root(Resource):
    def get(self):
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

api.add_resource(Root, '/')

class ListReleases(Resource):
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        parser.add_argument('offset', type=int, location='args')
        parser.add_argument('limit', type=int, location='args')
        parser.add_argument('value_gt', type=int, location='args')
        parser.add_argument('value_lt', type=int, location='args')
        args = parser.parse_args()
        print(args)
        releases = db.session.query(Release)
        releases_sum = db.session.query(func.sum(Release.value).label('sum'))

        if args['q'] != None:
            select_stmt = select([Release]).where(func.to_tsvector('english', Release.description).match(args['q'].replace(" ", "&"), postgresql_regconfig='english'))
            releases = releases.select_entity_from(select_stmt)
            releases_sum = releases_sum.select_entity_from(select_stmt)

        if args['value_gt'] != None:
            releases = releases.filter(Release.value >= args['value_gt'])
            releases_sum = releases_sum.filter(Release.value >= args['value_gt'])

        if args['value_lt'] != None:
            releases = releases.filter(Release.value <= args['value_lt'])
            releases_sum = releases_sum.filter(Release.value <= args['value_lt'])

        release_count = releases.count()
        #release_sum = releases.query(func.sum(Release.value).label('sum'))

        (offset,limit) = (0,50)
        if args['offset'] != None:
            offset = args['offset']
        if args['limit'] != None:
            limit = args['limit']
        releases = releases[offset:limit]

        pagination = {}
        pagination["offset"] = offset
        pagination["limit"] = limit
         
        output = {}
        output["meta"] = {}
        output["meta"]["count"] = release_count
        output["meta"]["total_value"] = releases_sum.scalar()
        output["meta"]["pagination"] = pagination
        output["releases"] = [] 
        for release in releases:
            output["releases"].append(release.json)
        return output 

api.add_resource(ListReleases, '/releases')

class IndividualRelease(Resource):
    def get(self,ocid):
        try:
            my_release = Release.query.filter_by(ocid=ocid).one()
            return my_release.json
        except NoResultFound:
            abort(404, message="Release {} does not exist".format(ocid)) 

api.add_resource(IndividualRelease, '/release/<string:ocid>')

class BuyerList(Resource):
    def get(self):
        buyers = db.session.query(Buyer.buyer_uid, Buyer.buyer_name).all()
        return [row._asdict() for row in buyers] 
        

api.add_resource(BuyerList, '/buyers')

if __name__ == '__main__':
    app.run()


