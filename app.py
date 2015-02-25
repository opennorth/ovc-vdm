from flask import Flask, render_template
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import reqparse, abort, Api, Resource
from sqlalchemy.orm.exc import *
from sqlalchemy.sql import func
from sqlalchemy import select,cast, desc, asc
from werkzeug.exceptions import NotAcceptable
import ho.pisa as pisa 
from StringIO import *
import os
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from datetime import datetime


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class unaccent(ReturnTypeFromArgs):
    pass


class CustomApi(Api):
    FORMAT_MIMETYPE_MAP = {
        "csv": "text/csv",
        "json": "application/json",
        "pdf": "application/pdf",
        "ocds": "application/json"
        # Add other mimetypes as desired here
    }

    def mediatypes(self):
        """Allow all resources to have their representation
        overriden by the `format` URL argument"""

        preferred_response_type = []
        format = request.args.get("format")
        if format:
            mimetype = self.FORMAT_MIMETYPE_MAP.get(format)
            preferred_response_type.append(mimetype)
            if not mimetype:
                raise NotAcceptable()
        return preferred_response_type + super(CustomApi, self).mediatypes()


app = Flask(__name__)
api = CustomApi(app)

#use env variable to get what type of environment we have
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)

from models import *


@api.representation('application/pdf')
def output_csv(data, code, headers=None):
    html = render_template('pdf_generator.html')

    output_pdf = StringIO()
    pisa.CreatePDF(html.encode('utf-8'), output_pdf)

    resp = app.make_response(output_pdf.getvalue())
    return resp


@api.representation('text/csv')
def output_csv(data, code, headers=None):
    #some CSV serialized data
    #print(data)
    rt = "\n"
    str = ","
    total = []
    for release in data["releases"]:
        laliste = []
        laliste.append(release["awards"][0]["itemsAwarded"][0]["classificationDescription"])
        laliste.append(release["awards"][0]["suppliers"][0]["id"]["name"])
        laliste.append(release["buyer"]["id"]["name"])
        row = str.join(laliste)
        total.append(row)

    data = rt.join(total)
    resp = app.make_response(data)
    return resp


class Root(Resource):
    def get(self):
        accept_header = request.headers.get('Accept')
        print(accept_header)
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
api.add_resource(Root, '/api/')

#should move this in an utils
def date_time_arg (value):
    #TODO SEE how to reject if not format YYYY-MM-DD
    return datetime.strptime(value, "%Y-%m-%d") 


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
        buyers = db.session.query(Buyer.buyer_uid, Buyer.buyer_name).all()
        return [row._asdict() for row in buyers] 
        

api.add_resource(BuyerList, '/api/buyers')

if __name__ == '__main__':
    app.run()


