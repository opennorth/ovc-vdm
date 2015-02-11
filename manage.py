from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from sqlalchemy.sql import exists
from sqlalchemy import or_
import os
import json
from models import *

from app import app, db
app.config.from_object('config.DevelopmentConfig')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def flushReleases():
    db.session.query(Release).filter(Release.langage == '').delete() 

@manager.command
def loadOcds(path):
    json_raw = open(path)
    data = json.load(json_raw)
    for release in data["releases"]:
        try:
            the_release= Release(release)

            the_buyer =  db.session.query(Buyer).filter(or_(Buyer.buyer_uid == release["buyer"]["id"]["uid"], Buyer.buyer_name== release["buyer"]["id"]["name"])).scalar()
            if the_buyer == None:
                the_buyer = Buyer(release["buyer"]) 
                db.session.add(the_buyer)
        
            the_buyer.releases.append(the_release)

	    for award in release["awards"]:
                the_release.awards.append(Award(award))
            db.session.add(the_release)
        except:
            print "meuh"
    db.session.commit()

if __name__ == '__main__':
    manager.run()
