from app import db
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy import Table, Column, Integer, ForeignKey, cast
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from slugify import slugify

import json


#TODO Move this to utils 
# Add SQL function 'width_bucket'
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.ext.compiler import compiles
class width_bucket(FunctionElement):
    name = 'width_bucket'

@compiles(width_bucket)
def compile(element, compiler, **kw):
    return "width_bucket(%s)" % compiler.process(element.clauses)



#db.Model works like a declarative_base
class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(db.String())
    mapper = db.Column(db.String())
    url =  db.Column(db.String())
    last_update = db.Column(db.DateTime(), default='2000-01-01 00:00:00')
    last_retrieve = db.Column(db.DateTime(), default='2000-01-01 00:00:00')

    releases = relationship("Release", cascade="delete", backref=backref("sources"))

    def __init__(self, data):
        self.name = data["name"]
        self.mapper = data["mapper"]
        self.url = data["url"]

    def __repr__(self):
        return '<name {}>'.format(self.name)


class Buyer(db.Model):
    __tablename__ = 'buyers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    slug = db.Column(db.String())
    json =  db.Column(JSON)

    releases = relationship("Release", backref="buyers")

    def __init__(self, json_data):
        self.json = json_data
        self.name = json_data["name"]
        self.slug = slugify(self.name, to_lower=True)


    def __repr__(self):
        return '<Buyer{ }>'.format(self.buyer_name)



class Release(db.Model):
    __tablename__ = 'releases'
    id = db.Column(Integer, primary_key=True)
    ocid = db.Column(db.String())
    language = db.Column(db.String())
    json =  db.Column(JSON)
    supplier = db.Column(db.String())
    supplier_slug = db.Column(db.String())
    dossier = db.Column(db.String())
    decision = db.Column(db.String())
    activities =  db.Column(ARRAY(db.String()))
    description = db.Column(db.String())
    concat = db.Column(db.String())
    date = db.Column(db.DateTime())
    value = db.Column(db.Float())
    #awards = relationship("Award", backref="releases", cascade="all, delete, delete-orphan")

    buyer_id = Column(db.Integer, ForeignKey('buyers.id'))
    source_id = Column(db.Integer, ForeignKey('sources.id'))



    def __init__(self, json_data):
        self.json = json_data
        self.ocid = json_data["ocid"]
        self.language = json_data["language"]

        self.supplier = json_data["awards"][0]["suppliers"][0]["name"]
        self.supplier_slug = slugify(self.supplier, to_lower=True)
        self.dossier = json_data["id"]
        self.decision = json_data["tender"]["items"][0]["id"]
        self.description = json_data["tender"]["description"]
        self.activities = json_data["tender"]["title"].split(";")
        self.date = json_data["date"]
        self.value = json_data["awards"][0]["value"]["amount"]

        self.concat = " ".join([self.supplier, self.dossier, self.decision, self.description, json_data["buyer"]["name"]]) 

    def __repr__(self):
        return '<ocid {}>'.format(self.ocid)

    @staticmethod
    def group_by_supplier():
        q = db.session.query(
        Release.supplier,
        func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
        q = q.group_by(Release.supplier)
        q = q.order_by('total_value DESC')

        #print (q)

        releases_by_buyer = []
        for supplier in q:
            releases_by_buyer.append({"supplier_name": supplier.supplier, "total_value" :  supplier.total_value, "count" : supplier.count })


        return releases_by_buyer

    @staticmethod
    def group_by_buyer():
        q = db.session.query(
        Buyer.name.label('buyer'),
        func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
        q = q.filter(Buyer.id == Release.buyer_id)
        q = q.group_by(Buyer.name)
        q = q.order_by('total_value DESC')



        releases_by_buyer = []
        for buyer in q:
            releases_by_buyer.append({"buyer_name": buyer.buyer, "total_value" :  buyer.total_value, "count" : buyer.count })


        return releases_by_buyer

    @staticmethod
    def group_by_value_range():
        q = db.session.query(
        width_bucket(Release.value, 0, 1000000, 19).label('segment'),
        func.sum(Release.value).label('total_value'), func.count(Release.value).label('count'))
        q = q.group_by('1')
        q = q.order_by('1')

        print (q)


        releases_by_value_range = []
        for row in q:
            releases_by_value_range.append({"segment": row.segment, "total_value" :  row.total_value, "count" : row.count })


        return releases_by_value_range



    @staticmethod
    def group_by_month():
        q = db.session.query(
        func.substring(cast(Release.date, db.String), 0,8).label('month'), func.count(Release.value).label('count'), func.sum(Release.value).label('total_value'))
        q = q.group_by("month")
        q = q.order_by("month")

        #print (q)

        releases_by_month = []
        for supplier in q:
            releases_by_month.append({"month": supplier.month, "total_value" :  supplier.total_value, "count" : supplier.count })


        return releases_by_month        