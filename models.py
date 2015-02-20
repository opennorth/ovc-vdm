from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


import json

#db.Model works like a declarative_base
class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(db.String())
    mapper = db.Column(db.String())
    url =  db.Column(db.String())
    last_update = db.Column(db.DateTime(), default='2000-01-01 00:00:00')

    releases = relationship("Release", cascade="all,delete", backref="sources")

    def __init__(self, data):
        self.name = data["name"]
        self.mapper = data["mapper"]
        self.url = data["url"]

    def __repr__(self):
        return '<name {}>'.format(self.name)


class Buyer(db.Model):
    __tablename__ = 'buyers'

    buyer_uid = db.Column(db.Integer, primary_key=True)
    buyer_name = db.Column(db.String())
    json =  db.Column(JSON)

    releases = relationship("Release", backref="buyers")

    def __init__(self, json_data):
        self.json = json_data
        #self.buyer_uid= json_data["id"]["uid"]
        self.buyer_name = json_data["id"]["name"]

    def __repr__(self):
        return '<Buyer{ }>'.format(self.buyer_name)


class Release(db.Model):
    __tablename__ = 'releases'
    id = db.Column(Integer, primary_key=True)
    ocid = db.Column(db.String())
    language = db.Column(db.String())
    json =  db.Column(JSON)
    description = db.Column(db.String())
    value = db.Column(db.Float())
    #awards = relationship("Award", backref="releases", cascade="all, delete, delete-orphan")

    buyer_id = Column(db.Integer, ForeignKey('buyers.buyer_uid'))
    source_id = Column(db.Integer, ForeignKey('sources.id'))

    def __init__(self, json_data):
        self.json = json_data
        self.ocid = json_data["ocid"]
        self.language = json_data["language"]
        self.value = json_data["awards"][0]["awardValue"]["amount"]

        the_description = json_data["awards"][0]["suppliers"][0]["id"]["name"]
        the_description += " " + json_data["buyer"]["id"]["name"]
        the_description += " " + json_data["formation"]["itemsToBeProcured"][0]["classificationDescription"]
        the_description += " " + json_data["formation"]["itemsToBeProcured"][0]["description"]
        self.description = the_description 
    def __repr__(self):
        return '<ocid {}>'.format(self.ocid)
