from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from app import db
import json
from nose.tools import *
from manage import update_sources, update_releases
import subprocess

#init_db()

import app
test_app = app.app.test_client()

def setup_module(module):
    print ("setup module")
    db.drop_all()
    db.create_all()

    subprocess.call(["psql -c \"CREATE INDEX idx_fts_fr_concat_releases ON releases USING gin(to_tsvector('fr', concat));\""], shell=True)

    update_sources()
    update_releases()



def teardown_module(module):
    print ("Teardown_module")
    db.drop_all()

def test_api_root():
  rv = test_app.get('/api/')
  eq_(rv.status_code,200)
  resp = json.loads(rv.data)

  eq_(resp["releases"]["count"],9)
