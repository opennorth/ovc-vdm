import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'] 

class ProductionConfig(Config):
    DEBUG = False
    DATA_URL = ['http://donnees.ville.montreal.qc.ca/dataset/74efbfc7-b1bd-488f-be6f-ad122f1ebe8d/resource/a7c221f7-7472-4b01-9783-ed9e847ee8c1/download/20142015contratsfonctionnairesvillecentrale.csv']

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DATA_URL = ['http://donnees.ville.montreal.qc.ca/dataset/74efbfc7-b1bd-488f-be6f-ad122f1ebe8d/resource/a7c221f7-7472-4b01-9783-ed9e847ee8c1/download/20142015contratsfonctionnairesvillecentrale.csv']

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DATA_URL = ['http://donnees.ville.montreal.qc.ca/dataset/74efbfc7-b1bd-488f-be6f-ad122f1ebe8d/resource/a7c221f7-7472-4b01-9783-ed9e847ee8c1/download/20142015contratsfonctionnairesvillecentrale.csv']


class TestingConfig(Config):
    TESTING = True
