from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy.sql import exists
from sqlalchemy import or_
from sqlalchemy.orm import exc
from mapper import Mapper
import email.utils as eut
import datetime
import requests
import os
import json
from models import *

from app import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def flush_releases():
    #TODO: APPLIQUER CASCADE LORS DE LA CREATION DES RELEASES
    try:
        db.session.query(Release).delete() 
        db.session.commit()
    except sqlalchemy.exc:
        db.session.rollback()

@manager.command
def update_sources():
    #TODO : Delete sources that have been removed from config
    try:
        for config_source in  app.config["DATA_SOURCES"]:
            db_source =  db.session.query(Source).filter(Source.url == config_source["url"]).scalar()
            if db_source == None:
                db_source = Source(config_source) 
                db.session.add(db_source)            
    except TypeError as e:
       print "Typer error: %s" %  repr(e)
    except exc.FlushError as e:  
       db.session.rollback()
       print "sqlalchemy error: %s" %  repr(e)


    db.session.commit()


@manager.command
def update_releases():
    '''Uses the sources list in DB to search for contracts'''
    sources =  db.session.query(Source).all()

    for source in sources:
        print source.url
        r = requests.get(source.url)

        #If Last-Modified not avaiable, we always process
        now = datetime.datetime.now()
        source_update = now
        if 'Last-Modified' in r.headers:
            source_update = datetime.datetime(*eut.parsedate(r.headers['Last-Modified'])[:6])

        if source_update >= source.last_update:
            load_source(source.url, source.mapper)
       

@manager.command
def load_source(path, mapper_type):
    mapper = Mapper(path, mapper_type)
    output = mapper.to_ocds()
    load_ocds(output, type='dict')

@manager.command
def load_ocds(ocds, type='path'):
    data = {}
    if type == 'path':
        data = json.load(open(ocds))
    else:
        data = ocds

    try:
        for release in data["releases"]:
        
            the_release= Release(release)

            the_buyer =  db.session.query(Buyer).filter(Buyer.buyer_name== release["buyer"]["id"]["name"]).scalar()
            if the_buyer == None:
                the_buyer = Buyer(release["buyer"]) 
                db.session.add(the_buyer)
        
            the_buyer.releases.append(the_release)

	    #for award in release["awards"]:
        #        the_release.awards.append(Award(award))
            db.session.add(the_release)
    except TypeError as e:
        db.session.rollback()
        print "Typer error: %s" %  repr(e)
    except exc.FlushError as e:  
        db.session.rollback()
        print "sqlalchemy error: %s" %  repr(e)


    db.session.commit()

if __name__ == '__main__':
    manager.run()
