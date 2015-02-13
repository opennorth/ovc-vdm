from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy.sql import exists
from sqlalchemy import or_
from mapper import Mapper
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
def load_source(path):
    current_mapper = Mapper(path)
    output = current_mapper.csv_mapper()
    load_ocds(output, type='dict')

@manager.command
def load_ocds(ocds, type='path'):
    data = {}
    if type == 'path':
        data = json.load(open(ocds))
    else:
        data = ocds

    for release in data["releases"]:
        try:
            the_release= Release(release)

            the_buyer =  db.session.query(Buyer).filter(Buyer.buyer_name== release["buyer"]["id"]["name"]).scalar()
            if the_buyer == None:
                the_buyer = Buyer(release["buyer"]) 
                db.session.add(the_buyer)
        
            the_buyer.releases.append(the_release)

	    #for award in release["awards"]:
        #        the_release.awards.append(Award(award))
            db.session.add(the_release)
        except TypeError:
            print "meuh"
    db.session.commit()

if __name__ == '__main__':
    manager.run()
