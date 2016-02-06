# -*- coding: utf-8 -*-
from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import json
from nose.tools import *
from manage import update_sources, update_releases, generate_stats
import subprocess
import os
from app import db
import time
from models import *


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

  eq_(resp["releases_count"],18)

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
      # Test parameter order by buyer asc
      'url': 'api/releases?&order_by=buyer&order_dir=asc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 9,
       'value':1126244
       },
      {
      # Test parameter order by supplier desc
      'url': 'api/releases?&order_by=supplier&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 9,
       'value':828186
       },       
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
      # q with "invalid" chars
      'url': 'api/releases?q=construction()_    de&order_by=value&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'response': 200,
       'count': 2,
       'value':798556
       },        
       {
      # Test parameter q and highlight sur description
      'url': 'api/releases?q=dickson&highlight=True', 
       'json_path' : ("releases",0,"awards",0,"items",0,"description"),
       'response': 200,
       'count': 1,
       'value': 'ACCORDER UN CONTRAT À PROCOVA INC. POUR LA MISE AUX NORMES DES SÉPARATEURS D\'HUILE AU GARAGE <em>DICKSON</em> (0434) - DÉPENSE TOTALE DE 903 979,44 $, TAXES INCLUSES - APPEL D\'OFFRES PUBLIC 5598 - TROIS SOUMISSIONNAIRES.'
       },        
       {
      # Test parameter q and highlight sur fournisseur
      'url': 'api/releases?q=LOUISBOURG&highlight=True', 
       'json_path' : ("releases",0,"awards",0,"suppliers",0,"name"),
       'response': 200,
       'count': 1,
       'value': '<em>LOUISBOURG</em> SBC S.E.C'
       },  
       {
      # Test parameter q and highlight sur fournisseur
      'url': 'api/releases?q=ROXBORO&highlight=True', 
       'json_path' : ("releases",0,"buyer","name"),
       'response': 200,
       'count': 1,
       'value': 'ARRONDISSEMENT DE PIERREFONDS-<em>ROXBORO</em>'
       },
       {
      # Test parameter q and NO highlight sur fournisseur
      'url': 'api/releases?q=ROXBORO', 
       'json_path' : ("releases",0,"buyer","name"),
       'response': 200,
       'count': 1,
       'value': 'ARRONDISSEMENT DE PIERREFONDS-ROXBORO'
       },       
       {
      # Test parameter q and highlight sur numero de dossier
      'url': 'api/releases?q=CM12 0837&highlight=True', 
       'json_path' : ("releases",0,"awards",0,"items",0,"id"),
       'response': 200,
       'count': 1,
       'value': '<em>CM12</em> <em>0837</em>'
       },
       {
      # Test parameter q and highlight sur numero de dossier
      'url': 'api/releases?q=1126013036&highlight=True', 
       'json_path' : ("releases",0,"awards",0,"id"),
       'response': 200,
       'count': 1,
       'value': '<em>1126013036</em>'
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
      # multiple buyer
      'url': 'api/releases?buyer=arrondissement-de-pierrefonds-roxboro;service-des-infrastructures-du-transport-et-de-lenvironnement&order_by=value&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 5,
       'response': 200,
       'value':1966515
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
      # activity with shitty name
      'url': 'api/releases?type=subvention&activity=Sports, loisirs, culture et développement social', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 6,
       'response': 200,
       'value':62003
       },       
       {  
      # Multiple activity
      'url': 'api/releases?activity=Arrondissements;Environnement&order_by=value&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 5,
       'response': 200,
       'value':1966515
       },         
       {
      # procuring enttity
      'url': 'api/releases?procuring_entity=conseil-municipal&order_by=value&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 9,
       'response': 200,
       'value':25394603
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
      # multiple supplier
      'url': 'api/releases?supplier=construction-djl-inc;procova-inc&order_by=value&order_dir=desc', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 2,
       'response': 200,
       'value':888527
       },
       {  
      # supplier size
      'url': 'api/releases?supplier_size=3', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 1,
       'response': 200,
       'value':25394603
       },   
       {  
      # multiple supplier size
      'url': 'api/releases?supplier_size=3;2', 
       'json_path' : ("releases",0,"awards",0,"value","amount"),
       'count': 9,
       'response': 200,
       'value':828186

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
      # Group by supplier with self-join
      'url': 'api/releases/by_supplier?supplier_size=3', 
       'json_path' : ("releases",0,"total_value"),
       'response': 200,
       'count':1,
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



def test_supplier_slugs():
  '''Test parameter limit'''
  rv = test_app.get('api/helpers/supplier_slugs')
  eq_(rv.status_code,200)
  resp = json.loads(rv.data)
  eq_(len(resp["suppliers"]),18)


def test_buyer_slugs():
  '''Test parameter limit'''
  rv = test_app.get('api/helpers/buyer_slugs')
  eq_(rv.status_code,200)
  resp = json.loads(rv.data)
  eq_(len(resp["buyers"]),5)

def test_activity_colors():
  '''Test parameter limit'''
  rv = test_app.get('api/helpers/activity_list')
  eq_(rv.status_code,200)
  resp = json.loads(rv.data)
  eq_(len(resp["activities"]),18)

  for activity in resp["activities"]:
    if activity["name"] == "Arrondissements":
      eq_(activity["color_code"], "#DDA2A2")




def test_individual_release():
  '''Test parameter limit'''
  rv1 = test_app.get('api/releases?order_by=value&order_dir=desc')
  resp1 = json.loads(rv1.data)
  ocid = resp1["releases"][0]['ocid']


  rv2 = test_app.get('api/release/' + ocid + '?q=MCGILL&highlight=True')
  eq_(rv2.status_code,200)
  resp2 = json.loads(rv2.data)

  desc = "1- RÉSILIER LE BAIL INTERVENU ENTRE LA VILLE ET LA RÉGIE DE LA SANTÉ ET DES SERVICES SOCIAUX MONTRÉAL-CENTRE (CO98 00531). 2- RÉSILIER LE BAIL INTERVENU ENTRE LA VILLE ET LE CENTRE UNIVERSITAIRE <em>MCGILL</em> (CM11 0631). 3- APPROUVER LE NOUVEAU BAIL PAR LEQUEL LA VILLE LOUE, À L’AGENCE DE LA SANTÉ ET DES SERVICES SOCIAUX DE MONTRÉAL, POUR UNE DURÉE DE 9 ANS, À COMPTER DU 1ER OCTOBRE 2011, UN ESPACE SITUÉ AU 1301, RUE SHERBROOKE EST (PAVILLON LAFONTAINE), POUR DES FINS ADMINISTRATIVES MOYENNANT UNE RECETTE TOTALE DE 25 394 602,80 $ TPS INCLUSE. "
  eq_(resp2['awards'][0]['value']['amount'],25394603)
  eq_(resp2['awards'][0]['items'][0]['description'],desc)

def test_individual_release_error():
  '''Test parameter limit'''
  rv1 = test_app.get('api/releases?order_by=value&order_dir=desc')
  resp1 = json.loads(rv1.data)
  ocid = resp1["releases"][0]['ocid']

'''
def not_test_cache_etag():
  DISABLED - Test that cache and etag are working

  #Do a first request and get etag
  start = int(round(time.time() * 1000))
  rv1 = test_app.get('api/releases')
  first = int(round(time.time() * 1000)) - start

  etag = rv1.headers.get("etag")

  #Do a second request and check etag is the same
  start = int(round(time.time() * 1000))
  rv2 = test_app.get('api/releases')
  second = int(round(time.time() * 1000)) - start

  assert(second <= (first/1.5))
  eq_(etag, rv2.headers.get("etag"))

  #Third request with if-none-match should trigger a 304
  headers = [("If-None-Match", etag)]
  start = int(round(time.time() * 1000))
  rv3 = test_app.get('api/releases', headers=headers)
  third = int(round(time.time() * 1000)) - start

  eq_(rv3.status_code, 304)

  #For relead of source to change timestamp used for etag
  time.sleep(2)
  update_releases(forced=True)

  #Try again with if-none-match, but this time etag shoud have changed.
  #This time we should get a 200 with different etag
  headers = [("If-None-Match", etag)]
  start = int(round(time.time() * 1000))
  rv4 = test_app.get('api/releases', headers=headers)
  fourth = int(round(time.time() * 1000)) - start

  eq_(rv4.status_code, 200)
  assert(etag != rv4.headers.get("etag"))
'''

def test_pdf():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?q=construction&order_by=value&order_dir=desc&format=pdf')
  eq_(rv.status_code,200)

def test_csv():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?q=construction&order_by=value&order_dir=desc&format=csv')
  eq_(rv.status_code,200)

def test_xlsx():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?q=construction&order_by=value&order_dir=desc&format=xlsx')
  eq_(rv.status_code,200)

def test_ocds():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?q=construction&order_by=value&order_dir=desc&format=ocds')
  eq_(rv.status_code,200)

def test_too_records():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?limit=10000000')
  eq_(rv.status_code,400)

def test_invalid_format():
  '''Test parameter limit'''
  rv = test_app.get('api/releases?format=foo')
  eq_(rv.status_code,400)

def test_stats():
  generate_stats()


