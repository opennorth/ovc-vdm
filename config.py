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
            'type': 'contract'
        },
        {
            'name': 'Conseil d\'agglomeration',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/6df93670-af44-492e-a644-72643bf58bc0/resource/35e636c1-9f99-4adf-8898-67c2ea4f8c47/download/contratsconseilagglomeration.csv',
            'type': 'contract'
        },
        {
            'name': 'Conseil Muncipal',
            'mapper': 'field_mapper_subvention_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/067c3bf6-0ec0-4159-a582-b0d58b44491f/resource/3abb3596-45fb-4c80-8d6f-1633db5427d4/download/subventionsconseilmunicipal.csv',
            'type': 'subvention'
        }          
    ]

    SERVICE_TO_ACTIVITY = {
        "ARRONDISSEMENT DE MONTRÉAL-NORD": ["Arrondissements"],
        "ARRONDISSEMENT DE RIVIÈRE-DES-PRAIRIES–POINTE-AUX-TREMBLES": ["Arrondissements"],
        "ARRONDISSEMENT DE LASALLE" : ["Arrondissements"],
        "ARRONDISSEMENT DE PIERREFONDS-ROXBORO" : ["Arrondissements"],
        "ARRONDISSEMENT DE VERDUN": ["Arrondissements"],
        "ARRONDISSEMENT DE SAINT-LAURENT": ["Arrondissements"],
        "ARRONDISSEMENT LE SUD-OUEST": ["Arrondissements"],
        "ARRONDISSEMENT DE ROSEMONT-LA PETITE-PATRIE": ["Arrondissements"],
        "ARRONDISSEMENT DE SAINT-LÉONARD": ["Arrondissements"],
        "ARRONDISSEMENT DE VILLE-MARIE": ["Arrondissements"],
        "ARRONDISSEMENT DE LACHINE" : ["Arrondissements"],
        "ARRONDISSEMENT D'AHUNTSIC-CARTIERVILLE" : ["Arrondissements"],
        "ARRONDISSEMENT DE MERCIER-HOCHELAGA-MAISONNEUVE" : ["Arrondissements"],
        "ARRONDISSEMENT DE CÔTE-DES-NEIGES-NOTRE-DAME-DE-GRÂCE" : ["Arrondissements"],
        "ARRONDISSEMENT DE VILLERAY-SAINT-MICHEL-PARC-EXTENSION" : ["Arrondissements"],
        "SERVICE DES TECHNOLOGIES DE L'INFORMATION" : ["Gestion de l'information"],
        "SERVICE DE LA GESTION ET DE LA PLANIFICATION IMMOBILIÈRE": ["Organisation et administration"],
        "SERVICE DE POLICE DE MONTRÉAL": ["Sécurité publique"],
        "SERVICE DES INFRASTRUCTURES, DU TRANSPORT ET DE L'ENVIRONNEMENT" : ["Transport","Environnement"],
        "SERVICE DE CONCERTATION DES ARRONDISSEMENTS ET DES RESSOURCES MATÉRIELLES": ["Organisation et administration"],
        "SERVICE DE LA MISE EN VALEUR DU TERRITOIRE": ["Urbanisme et habitation"],
        "SERVICE DE LA QUALITÉ DE VIE" : ["Sports, loisirs, culture et développement social"],
        "SERVICE DE L'EAU" : ["Infrastructures"],
        "SERVICE DES AFFAIRES INSTITUTIONNELLES": ["Organisation et administration"],
        "SERVICE DES INFRASTRUCTURES, DE LA VOIRIE ET DES TRANSPORTS" : ["Infrastructures"],
        "DIRECTION GÉNÉRALE" : ["Organisation et administration"],
        "SERVICE DE L'ESPACE POUR LA VIE": ["Sports, loisirs, culture et développement social"],
        "SERVICE DE L'APPROVISIONNEMENT": ["Ressources matérielles et services"],
        "SERVICE DE LA DIVERSITÉ SOCIALE ET DES SPORTS" : ["Sports, loisirs, culture et développement social"],
        "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT ROYAL": ["Sports, loisirs, culture et développement social"],
        "SOCIÉTÉ DU PARC JEAN-DRAPEAU": ["Sports, loisirs, culture et développement social"],
        "SERVICE DE SÉCURITÉ INCENDIE DE MONTRÉAL" : ["Sécurité publique"],
        "SERVICE DES FINANCES" : ["Ressources financières"],
        "SERVICE DU CAPITAL HUMAIN ET DES COMMUNICATIONS" : ["Ressources humaines", "Communications et relations publiques"],
        "SERVICE DES AFFAIRES JURIDIQUES ET DE L’ÉVALUATION FONCIÈRE" : ["Juridique", "Foncier"],
        "BUREAU DU VÉRIFICATEUR GÉNÉRAL" : ["Organisation et administration"],
        "SERVICE DU MATÉRIEL ROULANT ET DES ATELIERS" : ["Ressources matérielles et services"],
        "SERVICE DES RESSOURCES HUMAINES": ["Ressources humaines"]

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
            'url': 'fixtures/contracts.csv',
            'type': 'contract'
        },
         {
            'name': 'Conseil Muncipal',
            'mapper': 'field_mapper_subvention_mtl',
            'url': 'fixtures/subventions.csv',
            'type': 'subvention'
        },       
    ]
