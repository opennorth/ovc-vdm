# -*- coding: utf-8 -*-
from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import json
from nose.tools import *
from manage import update_sources, update_releases
import subprocess
import os
from app import db


import app
test_app = app.app.test_client()

def setup_module(module):
    print ("setup module")
    db.drop_all()
    db.create_all()

    dbname =  os.environ['DATABASE_URL'].split()[-1]
    print dbname

    subprocess.call(["psql -c \"CREATE INDEX idx_fts_fr_concat_releases ON releases USING gin(to_tsvector('french', concat))\" -d %s ;" % (dbname)], shell=True)

    update_sources()
    update_releases()



def teardown_module(module):
    print ("Teardown_module")
    db.drop_all()

def test_api_root():
  rv = test_app.get('/api/')
  eq_(rv.status_code,200)
  resp = json.loads(rv.data)

  eq_(resp["releases"]["count"],18)

def test_generator():

    #list of conditions and expected outcome to generate tests
    params = [
      {
      # Test parameter order by date and offset and limit
      'url': 'api/releases?&order_by=date&order_dir=asc&limit=4&offset=1', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 9,
       'value':546456
       },
       {
      # Test parameter q and order by value asc
      'url': 'api/releases?q=construction&order_by=value&order_dir=asc', 
       'json_path' : ('releases',0,"awards",0,"value","amount"),
       'response': 200,
       'count': 2,
       'value':546456
       },        
       {
      # Test parameter q and order by value desc
      'url': 'api/releases?q=construction&order_by=value&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 2,
       'value':798556
       }, 
       {
      # Test parameter order by date and offset and limit
      'url': 'api/releases?&order_by=date&order_dir=desc&limit=8', 
       'json_path' : ("releases",7,"awards",0,"value","amount"),
       'response': 200,
       'value':546456
       },  
       {         
      # Value greater lower
      'url': 'api/releases?value_gt=1500000&value_lt=2000000', 
       'json_path' :("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 1,
       'value':1966515
       },  
       {         
      # date greater lower
      'url': 'api/releases?date_gt=2012-09-14&date_lt=2012-09-15', 
       'json_path' :("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 1,
       'value':25394603
       },
       {  
      # buyer
      'url': 'api/releases?buyer=arrondissement-de-pierrefonds-roxboro', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 1,
       'response': 200,
       'value':1126244
       }, 
       {  
      # activity
      'url': 'api/releases?activity=Arrondissements', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 1,
       'response': 200,
       'value':1126244
       }, 
       {  
      # supplier
      'url': 'api/releases?supplier=construction-djl-inc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 1,
       'response': 200,
       'value':546456
       },                                     
       {        
      # Test subvention filter
      'url': 'api/releases?type=subvention', 
       'json_path' : ("meta","count"),
       'response': 200,
       'value':9
       },   
       {        
      # Group by supplier
      'url': 'api/releases/by_supplier?order_by=total_value&order_dir=desc', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':9,
       'value':25394603
       },  
       {        
      # Group by buyer
      'url': 'api/releases/by_buyer?order_by=total_value&order_dir=desc', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':3,
       'value':27759569
       },  
       {                  
      # Group by procuring enttity
      'url': 'api/releases/by_procuring_entity', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':1,
       'value':33093163
       },  
       {                  
      # Group by procuring buckets of value
      'url': 'api/releases/by_value?bucket=0,1000000,1', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':2,
       'value':28487362
       },     
       {                  
      # Group by month
      'url': 'api/releases/by_month', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':1,
       'value':33093163
       }, 
       {                  
      # Group by activity
      'url': 'api/releases/by_activity?order_by=total_value&order_dir=desc', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':3,
       'value':27759569
       },       
       {
      # Treemap activity => buyer
      'url': 'api/treemap?parent=activity&child=buyer', 
       'json_path' : ("releases",0,"children",0,"total_value"),
       'response': 200,
       'count':3,
       'value':27759569
       },  
       {
      # Treemap buyer => supplier
      'url': 'api/treemap?parent=buyer&child=supplier&activity=Transport', 
       'json_path' : ("releases",0,"children",0,"total_value"),
       'response': 200,
       'count':1,
       'value':1966515
       },          
       {
      # Treemap buyer => supplier
      'url': 'api/treemap?parent=size&child=supplier', 
       'json_path' : ("releases",0,"children",0,"total_value"),
       'response': 200,
       'count':2,
       'value':25394603
       },
       {
      # Invalide order by
      'url': 'api/releases?type=subvention&order_dir=ddejsy', 
       'response': 400,
       },         
    ]

    for item in params:
      yield call_api, item

def call_api(item):
    rv = test_app.get(item["url"])
    eq_(rv.status_code,item["response"])

    resp = json.loads(rv.data)

    if "count" in item:
      eq_(resp['meta']['count'],item["count"])

    if 'json_path' in item:
      #Get the value in the response located by path
      result = reduce(lambda d,key: d[key],item["json_path"], resp)
      eq_(result,item["value"])



def test_releases_pagination_2():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?&order_by=date&order_dir=asc&limit=4&offset=1')
  resp = json.loads(rv.data)
  eq_(len(resp["releases"]),4)


def test_individual_release():
  '''Test parameter limit'''
  rv1 = test_app.get('api/releases?order_by=value&order_dir=desc')
  resp1 = json.loads(rv1.data)
  ocid = resp1["releases"][0]['ocid']


  rv2 = test_app.get('api/release/' + ocid)
  eq_(rv2.status_code,200)
  resp2 = json.loads(rv2.data)
  eq_(resp2['awards'][0]['value']['amount'],25394603)

def test_individual_release_error():
  '''Test parameter limit'''
  rv1 = test_app.get('api/releases?order_by=value&order_dir=desc')
  resp1 = json.loads(rv1.data)
  ocid = resp1["releases"][0]['ocid']


  rv2 = test_app.get('api/release/' + ocid + '_')
  eq_(rv2.status_code,404)

