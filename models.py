# -*- coding: utf-8 -*-
from app import db
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy import Table, Column, Integer, ForeignKey, cast
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from slugify import slugify
from datetime import datetime
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
    skip_lines = db.Column(Integer)
    type = db.Column(db.String())
    last_update = db.Column(db.DateTime(), default='2000-01-01 00:00:00')
    last_retrieve = db.Column(db.DateTime(), default='2000-01-01 00:00:00')

    releases = relationship("Release", cascade="delete", backref=backref("sources"))

    def __init__(self, data):
        self.name = data["name"]
        self.mapper = data["mapper"]
        self.url = data["url"]
        self.type = data["type"]

        if 'skip_lines' in data:
            self.skip_lines = data["skip_lines"]

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
        return '<Buyer{ }>'.format(self.slug)


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String())
    name = db.Column(db.String())
    size =  db.Column(db.Integer)


    releases = relationship("Release", backref="suppliers")

    def __init__(self, json_data):
        self.name = json_data["name"]
        self.slug = slugify(self.name, to_lower=True)


    def __repr__(self):
        return '<Supplier{ }>'.format(self.name)


class Release(db.Model):
    __tablename__ = 'releases'
    id = db.Column(Integer, primary_key=True)
    ocid = db.Column(db.String())
    language = db.Column(db.String())
    json =  db.Column(JSON)
    procuring_entity = db.Column(db.String())
    procuring_entity_slug = db.Column(db.String())
    dossier = db.Column(db.String())
    decision = db.Column(db.String())
    activities =  db.Column(ARRAY(db.Text()))
    description = db.Column(db.String())
    concat = db.Column(db.String())
    date = db.Column(db.DateTime(), index=True)
    value = db.Column(db.Float(), index=True)
    type = db.Column(db.String(), index=True)

    buyer_id = Column(db.Integer, ForeignKey('buyers.id'))
    supplier_id = Column(db.Integer, ForeignKey('suppliers.id'))
    source_id = Column(db.Integer, ForeignKey('sources.id'))



    def __init__(self, json_data):
        self.json = json_data
        self.ocid = json_data["ocid"]
        self.language = json_data["language"]

        self.procuring_entity = json_data["tender"]["procuringEntity"]["name"]
        self.procuring_entity_slug = json_data["tender"]["procuringEntity"]["identifier"]["id"]
        self.dossier = json_data["awards"][0]["id"]
        self.decision = json_data["awards"][0]["items"][0]["id"]
        self.description = json_data["awards"][0]["items"][0]["description"]
        self.activities = json_data["subject"]
        self.date = json_data["date"]
        self.value = json_data["awards"][0]["value"]["amount"]
        self.type = json_data["tender"]["procurementMethodRationale"]

        self.concat = " ".join([json_data["awards"][0]["suppliers"][0]["name"], json_data["buyer"]["name"], self.dossier, self.decision, self.description]) 

    def __repr__(self):
        return '<ocid {}>'.format(self.ocid)


class DailyStat(db.Model):
    __tablename__ = 'daily_stats'
    id = db.Column(Integer, primary_key=True)
    datetime = db.Column(db.DateTime())
    path = db.Column(db.String())
    args =  db.Column(JSON)
    referrer = db.Column(db.String())



    def __init__(self, request):
        self.datetime = datetime.now()
        self.path = request.path
        self.args = request.args
        self.referrer = request.referrer


    def __repr__(self):
        return '<DailyStat {}>'.format(self.id)

class Stat(db.Model):
    __tablename__ = 'stats'
    id = db.Column(Integer, primary_key=True)
    date = db.Column(db.Date())
    total_counts = db.Column(Integer)
    referrers = db.Column(JSON)
    counts_app = db.Column(Integer)
    path = db.Column(JSON)
    args =  db.Column(JSON)



    def __repr__(self):
        return '<DailyStat {}>'.format(self.id)              
      