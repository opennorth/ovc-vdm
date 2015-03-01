import os
from flask import Flask, render_template, request, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource
from sqlalchemy.orm.exc import *
from sqlalchemy.sql import func

from sqlalchemy import select,cast, desc, asc
from datetime import datetime
from utils import date_time_arg,  unaccent

from werkzeug.exceptions import NotAcceptable
from flask.ext.restful import reqparse, abort, Api
from serializations import CustomApi, generate_pdf, generate_csv, generate_xlsx

#Initiate the APP
import sys
reload(sys)
sys.setdefaultencoding('utf-8')




app = Flask(__name__)
api = CustomApi(app)

app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)

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

from models import *

#Define routes for HTML content
@app.route("/")
def index():
    print (app.url_map)
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
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        parser.add_argument('offset', type=int, location='args')
        parser.add_argument('limit', type=int, location='args')
        parser.add_argument('value_gt', type=int, location='args')
        parser.add_argument('value_lt', type=int, location='args')
        parser.add_argument('date_gt', type=date_time_arg, location='args')
        parser.add_argument('date_lt', type=date_time_arg, location='args')        
        parser.add_argument('buyer', type=str, location='args')
        parser.add_argument('activity', type=str, location='args')
        parser.add_argument('supplier', type=str, location='args')
        parser.add_argument('order_by', type=str, location='args')
        parser.add_argument('order_dir', type=str, location='args')                         
        args = parser.parse_args()
        #print(args)
        releases = db.session.query(Release)
        releases_sum = db.session.query(func.sum(Release.value).label('sum'))

        #TODO: REFACTOR process of filtering parameters
        if args['q'] != None:
            select_stmt = select([Release]).where(func.to_tsvector('fr', unaccent(Release.description)).match(args['q'].replace(" ", "&"), postgresql_regconfig='fr'))
            releases = releases.select_entity_from(select_stmt)
            releases_sum = releases_sum.select_entity_from(select_stmt)

        if args['value_gt'] != None:
            releases = releases.filter(Release.value >= args['value_gt'])
            releases_sum = releases_sum.filter(Release.value >= args['value_gt'])


        if args['value_lt'] != None:
            releases = releases.filter(Release.value <= args['value_lt'])
            releases_sum = releases_sum.filter(Release.value <= args['value_lt'])

        if args['date_gt'] != None:
            releases = releases.filter(Release.date >= args['date_gt'])
            releases_sum = releases_sum.filter(Release.date >= args['date_gt'])


        if args['date_lt'] != None:
            releases = releases.filter(Release.date <= args['date_lt'])
            releases_sum = releases_sum.filter(Release.date <= args['date_lt'])

        if args['buyer'] != None:
            releases = releases.join(Buyer).filter(Buyer.slug == args['buyer'])
            releases_sum = releases_sum.join(Buyer).filter(Buyer.slug == args['buyer'])

        if args['activity'] != None:
            select_stmt = select([Release]).where(Release.activities.any(args['activity']))
            releases = releases.select_entity_from(select_stmt)
            releases_sum = releases_sum.select_entity_from(select_stmt)

        if args['supplier'] != None:
            releases = releases.filter(Release.supplier_slug == args['supplier'])
            releases_sum = releases_sum.filter(Release.supplier_slug == args['supplier'])            

        #TODO: Catch if order_by et order_dir n'ont pas les bonnes valeurs
        if (args['order_by'] != None):
            sort_attr = getattr(Release, args['order_by'])

            sorter = sort_attr.asc()
            if ('order_dir' in args and args['order_dir'] == 'desc'):
                sorter = sort_attr.desc()

            releases = releases.order_by(sorter)

        release_count = releases.count()

        (offset,limit) = (0,50)
        if args['offset'] != None:
            offset = args['offset']
        if args['limit'] != None:
            limit = args['limit']
        releases = releases[offset:limit]

        pagination = {"offset" : offset, "limit":  limit}

        output = {}
        
        if request.args.get("format") != 'ocds':
            
            output["meta"] = {}
            output["meta"]["count"] = release_count
            output["meta"]["total_value"] = releases_sum.scalar()
            output["meta"]["pagination"] = pagination

        output["uri"] = request.url

        #TODO: Ideally it would be the date of the last contract added
        output["publishedDate"] = datetime.now().isoformat()
 
        #TODO: MOVE THAT ELSE WHERE... IT'S STATIC STUFF       
        output["license"] = app.config["LICENSE"]
        output["publicationPolicy"] = app.config["PUBLICATION_POLICY"]

        #publisher section 
        output["publisher"] = {}
        output["publisher"]["identifier"] = {
                "legalName" :  app.config["PUBLISHER_LEGAL_NAME"]}

        output["publisher"]["name"] =  app.config["PUBLISHER_NAME"]

        output["publisher"]["address"] = {
                "streetAddress" : app.config["PUBLISHER_ADDRESS"][0],
                "locality" : app.config["PUBLISHER_ADDRESS"][1],
                "region" : app.config["PUBLISHER_ADDRESS"][2],
                "postalCode" : app.config["PUBLISHER_ADDRESS"][3],
                "countryName" : app.config["PUBLISHER_ADDRESS"][4]
        }

        output["publisher"]["contactPoint"] = {
                "name" : app.config["PUBLISHER_CONTACT"][0],
                "email" : app.config["PUBLISHER_CONTACT"][1],
                "telephone" : app.config["PUBLISHER_CONTACT"][2],
                "faxNumber" : app.config["PUBLISHER_CONTACT"][3],
                "url" : app.config["PUBLISHER_CONTACT"][4]
        }

        output["releases"] = [] 
        for release in releases:
            output["releases"].append(release.json)
        return output 

api.add_resource(ListReleases, '/api/releases')

class IndividualRelease(Resource):
    def get(self,ocid):
        try:
            my_release = Release.query.filter_by(ocid=ocid).one()
            return my_release.json
        except NoResultFound:
            abort(404, message="Release {} does not exist".format(ocid)) 

api.add_resource(IndividualRelease, '/api/release/<string:ocid>')

class BuyerList(Resource):
    def get(self):

        parser = reqparse.RequestParser()   
        parser.add_argument('offset', type=int, location='args')
        parser.add_argument('limit', type=int, location='args')                           
        args = parser.parse_args(strict=True)

        buyers = db.session.query(Buyer.id, Buyer.name, Buyer.slug).all()
        return [row._asdict() for row in buyers] 
        

api.add_resource(BuyerList, '/api/buyers')

if __name__ == '__main__':
    app.run()


