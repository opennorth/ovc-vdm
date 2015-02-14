from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from app import db
import json
from nose.tools import *
from manage import load_source

#init_db()

import app
test_app = app.app.test_client()

def setup_module(module):
    print ("setup module")
    db.drop_all()
    db.create_all()
    load_source('fixtures/contracts.csv')



def teardown_module(module):
    print ("Teardown_module")
    db.drop_all()

def test_api_root():
  rv = test_app.get('/')
  eq_(rv.status_code,200)
  resp = json.loads(rv.data)

  eq_(resp["releases"]["count"],10)
