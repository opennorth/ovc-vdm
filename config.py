# -*- coding: utf-8 -*-
import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    URL_ROOT = 'http//localhost'
    OCID_PREFIX = 'ocds-a1234567-mt-'

    DATA_SOURCES = [
        {
            'name': 'Conseil Muncipal',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/6df93670-af44-492e-a644-72643bf58bc0/resource/a6869244-1a4d-4080-9577-b73e09d95ed5/download/contratsconseilmunicipal.csv',
        },
        {
            'name': 'Conseil d\'agglomeration',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/6df93670-af44-492e-a644-72643bf58bc0/resource/35e636c1-9f99-4adf-8898-67c2ea4f8c47/download/contratsconseilagglomeration.csv'
        },
        {
            'name': 'Comité executif',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/505f2f9e-8cec-43f9-a83a-465717ef73a5/resource/87a6e535-3a6e-4964-91f5-836cd31099f7/download/contratscomiteexecutif.csv'
        } 
    ]

    SERVICE_TO_ACTIVITY = {
        "ARRONDISSEMENT DE MONTRÉAL-NORD": ["Arrondissements"],
        "SERVICE DES TECHNOLOGIES DE L'INFORMATION" : ["Gestion de l'information"],
        "SERVICE DE LA GESTION ET DE LA PLANIFICATION IMMOBILIÈRE": ["Organisation et administration"],
        "ARRONDISSEMENT DE RIVIÈRE-DES-PRAIRIES–POINTE-AUX-TREMBLES": ["Arrondissements"],
        "ARRONDISSEMENT DE LASALLE" : ["Arrondissements"],
        "SERVICE DE POLICE DE MONTRÉAL": ["Sécurité publique"],
        "SERVICE DES INFRASTRUCTURES, DU TRANSPORT ET DE L'ENVIRONNEMENT" : ["Transport","Environnement"]
    }


class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    URL_ROOT = 'https://ovc-stage.herokuapp.com'
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    

class TestingConfig(Config):
    TESTING = True

    DATA_SOURCES = [
        {
            'name': 'Conseil Muncipal',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'fixtures/contracts.csv'
        }
    ]
