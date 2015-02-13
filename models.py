from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

import json


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

    ocid = db.Column(db.String(), primary_key=True)
    language = db.Column(db.String())
    json =  db.Column(JSON)
    description = db.Column(db.String())
    value = db.Column(db.Float())
    #awards = relationship("Award", backref="releases", cascade="all, delete, delete-orphan")

    buyer_id = Column(db.Integer, ForeignKey('buyers.buyer_uid'))

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
'''
class Award(db.Model):
    __tablename__ = 'awards'

    awardID = db.Column(db.String(), primary_key=True)
    awardDate = db.Column(db.Date())
    awardValue = db.Column(db.Integer)
    json =  db.Column(JSON)
    release_id = Column(db.String(), ForeignKey('releases.ocid'))


    def __init__(self, json_data):
        self.json = json_data
        self.awardID = json_data["awardID"]
        self.awardDate = json_data["awardDate"]
        self.awardValue= json_data["awardValue"]["amount"]
    def __repr__(self):
        return '<awardid {}>'.format(self.awardid)

'''