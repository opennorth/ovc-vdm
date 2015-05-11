# -*- coding: utf-8 -*-
import os


class Config(object):
    DEBUG = False
    TESTING = False
    SENDMAIL = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    if 'EMAIL_CREDENTIALS' in os.environ:
        EMAIL_CREDENTIALS = tuple(os.environ['EMAIL_CREDENTIALS'].split('@'))
    
    SMTP_SERVER = 'smtp.sendgrid.net'
    EMAIL_SENDER = 'ovc@opennorth.ca'
    ADMINS = ['stephane@opennorth.ca']

    URL_ROOT = 'http//localhost'
    OCID_PREFIX = 'ocds-a1234567-mt-'

    CACHE_DURATION = 86400
    STATS_LOG = 'stats/log.out'

    START_HIGHLIGHT = "<em>"
    END_HIGHLIGHT = "</em>"

    DATA_SOURCES = [
        {
            'name': 'Fonctionnaires',
            'mapper': 'field_mapper_fonc_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/74efbfc7-b1bd-488f-be6f-ad122f1ebe8d/resource/a7c221f7-7472-4b01-9783-ed9e847ee8c1/download/contratsfonctionnaires.csv',
            'type': 'contract'
        }, 
        {
            'name': 'Conseil Muncipal',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/6df93670-af44-492e-a644-72643bf58bc0/resource/a6869244-1a4d-4080-9577-b73e09d95ed5/download/contratsconseilmunicipal.csv',
            'type': 'contract'
        },
        {
            'name': 'Comité éxecutif',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/505f2f9e-8cec-43f9-a83a-465717ef73a5/resource/87a6e535-3a6e-4964-91f5-836cd31099f7/download/contratscomiteexecutif.csv',
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
        },
        {
            'name': 'Conseil d\'agglomeration',
            'mapper': 'field_mapper_subvention_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/067c3bf6-0ec0-4159-a582-b0d58b44491f/resource/bc862025-9735-4a10-8d29-a5ee6621277c/download/subventionsconseilagglomeration.csv',
            'type': 'subvention'
        },                
        {
            'name': 'Conseil Muncipal',
            'mapper': 'field_mapper_subvention_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/067c3bf6-0ec0-4159-a582-b0d58b44491f/resource/3abb3596-45fb-4c80-8d6f-1633db5427d4/download/subventionsconseilmunicipal.csv',
            'type': 'subvention'
        },
        {
            'name': 'Comité éxecutif',
            'mapper': 'field_mapper_subvention_mtl',
            'url': 'http://donnees.ville.montreal.qc.ca/dataset/4900f199-445f-4a89-a4e1-a02ee2391d26/resource/96c66e8d-f217-4249-8ff5-42ebac8045b9/download/subventionscomiteexecutif.csv',
            'type': 'subvention'
        },        
    ]

    SUPPLIER_SIZE = [0, 1000000, 10000000]

    ACTIVITY_COLOR_CODE = {
        "Infrastructures" : "#00ff00",
        "Organisation et administration" : "#ff0000",
        "Transport" : "#0000ff",
        "Sports, loisirs, culture et développement social" : "#ffff00",
        "Gestion de l'information" : "#ff00ff",
        "Immeubles et terrains" : "#114477",
        "Arrondissements": "#888888",
        "Autre" : "#00ffff",
        "Sécurité publique": "#888888",
        "Ressources matérielles et services": "#888888",
        "Urbanisme et habitation": "#888888",
        "Environnement": "#888888",
        "Ressources financières": "#888888",
        "Ressources humaines": "#888888",
        "Juridique": "#888888",
        "Développement économique": "#888888",
        "Communications et relations publiques": "#888888",
        "Foncier": "#888888"

    }

    SERVICE_TO_ACTIVITY = {
        # NO SEMI_COLUMN - PAS DE POINT-VIRGULE
        "ARRONDISSEMENT DE VILLERAY-SAINT-MICHEL-PARC-EXTENSION" : ["Arrondissements"],
        "ARRONDISSEMENT DE VILLE-MARIE": ["Arrondissements"],
        "ARRONDISSEMENT DE MONTRÉAL-NORD": ["Arrondissements"],
        "ARRONDISSEMENT DE MERCIER-HOCHELAGA-MAISONNEUVE": ["Arrondissements"],
        "ARRONDISSEMENT DE L’ÎLE-BIZARD–STE-GENEVIÈVE": ["Arrondissements"],
        "ARRONDISSEMENT DE LASALLE": ["Arrondissements"],
        "ARRONDISSEMENT DE LACHINE": ["Arrondissements"],
        "ARRONDISSEMENT DE SAINT-LAURENT": ["Arrondissements"],
        "ARRONDISSEMENT DE SAINT-LÉONARD": ["Arrondissements"],
        "ARRONDISSEMENT DE ROSEMONT-LA PETITE-PATRIE": ["Arrondissements"],
        "ARRONDISSEMENT DU PLATEAU-MONT-ROYAL": ["Arrondissements"],
        "ARRONDISSEMENT DE PIERREFONDS-ROXBORO": ["Arrondissements"],
        "ARRONDISSEMENT D'OUTREMONT": ["Arrondissements"],
        "ARRONDISSEMENT DU SUD-OUEST": ["Arrondissements"],
        "ARRONDISSEMENT DE RIVIÈRE-DES-PRAIRIES–POINTE-AUX-TREMBLES": ["Arrondissements"],
        "ARRONDISSEMENT DE CÔTE-DES-NEIGES - NOTRE-DAME-DE-GRÂCE": ["Arrondissements"],
        "ARRONDISSEMENT D'AHUNTSIC-CARTIERVILLE": ["Arrondissements"],
        "ARRONDISSEMENT D'ANJOU": ["Arrondissements"],
        "ARRONDISSEMENT DE VERDUN": ["Arrondissements"],
        "BUREAU DE L’OMBUDSMAN" :["Organisation et administration"],
        "BUREAU DU VÉRIFICATEUR GÉNÉRAL" :["Organisation et administration"],
        "BUREAU DE L'INSPECTEUR GÉNÉRAL" :["Organisation et administration"],
        "BUREAU DE LA VILLE INTELLIGENTE ET NUMÉRIQUE": ["Organisation et administration"],
        "COMMISSION DES SERVICES ÉLECTRIQUES DE MONTRÉAL" : ["Organisation et administration"],
        "COMMISSION DE LA FONCTION PUBLIQUE DE MONTRÉAL": ["Organisation et administration"],
        "DIRECTION GÉNÉRALE" : ["Organisation et administration"],
        "SERVICE DE LA MISE EN VALEUR DU TERRITOIRE" : ["Urbanisme et habitation"],
        "SERVICE DU DÉVELOPPEMENT ÉCONOMIQUE" : ["Développement économique"],
        "SERVICE DU MATÉRIEL ROULANT ET DES ATELIERS" : ["Ressources matérielles et services"],
        "SERVICE DES TECHNOLOGIES DE L'INFORMATION" : ["Gestion de l'information"],
        "SERVICE DES RESSOURCES HUMAINES" : ["Ressources humaines"],
        "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT-ROYAL": ["Sports, loisirs, culture et développement social"],
        "SERVICE DES ESPACES POUR LA VIE":  ["Sports, loisirs, culture et développement social"],
        "SERVICE DES AFFAIRES JURIDIQUES ET DE L'ÉVALUATION FONCIÈRE" : ["Juridique", "Foncier"],
        "SERVICE DE POLICE DE LA VILLE DE MONTRÉAL": ["Sécurité publique"],
        "SERVICE DE L'EAU" : ["Infrastructures"],
        "SERVICE DES INFRASTRUCTURES, DE LA VOIRIE ET DES TRANSPORTS" : ["Infrastructures"],
        "SERVICE DE LA GESTION ET DE LA PLANIFICATION IMMOBILIÈRE": ["Immeubles et terrains"],
        "SERVICE DE LA DIVERSITÉ SOCIALE ET DES SPORTS": ["Sports, loisirs, culture et développement social"],
        "SERVICE DE LA CONCERTATION DES ARRONDISSEMENTS ET RESSOURCES MATÉRIELLES": ["Organisation et administration"],
        "SERVICE DE L'APPROVISIONNEMENT" : ["Ressources matérielles et services"],
        "SERVICE DE L'ENVIRONNEMENT"  : ["Environnement"],
        "SERVICE DE L'ÉVALUATION FONCIÈRE" : ["Foncier"],
        "SERVICE DE LA CONCERTATION DES ARRONDISSEMENTS" : ["Organisation et administration"],
        "SERVICE DE LA CULTURE" : ["Sports, loisirs, culture et développement social"],
        "SERVICE DE LA PERFORMANCE ORGANISATIONNELLE" : ["Organisation et administration"],
        "SERVICE DE LA QUALITÉ DE VIE" : ["Sports, loisirs, culture et développement social"],
        "SERVICE DE SÉCURITÉ INCENDIE DE MONTRÉAL" : ["Sécurité publique"],
        "SERVICE DES AFFAIRES INSTITUTIONNELLES" : ["Organisation et administration"],
        "SERVICE DES AFFAIRES JURIDIQUES" : ["Juridique"],
        "SERVICE DES COMMUNICATIONS" : ["Communications et relations publiques"],
        "SERVICE DES FINANCES" : ["Ressources financières"],
        "SERVICE DES INFRASTRUCTURES, DU TRANSPORT ET DE L'ENVIRONNEMENT" : ["Transport","Environnement"],
        "SERVICE DU CAPITAL HUMAIN ET DES COMMUNICATIONS" : ["Ressources humaines", "Communications et relations publiques"],
        "SERVICE DU CONTRÔLEUR GÉNÉRAL" : ["Organisation et administration"],
        "SERVICE DU GREFFE" : ["Gestion de l'information"],
        "SERVICE DES INFRASTRUCTURES, DE LA VOIRIE ET DES TRANSPORTS" : ["Infrastructures"],
        "SERVICE DE LA CONCERTATION DES ARRONDISSEMENTS ET RESSOURCES MATÉRIELLES": ["Organisation et administration"],
        "SOCIÉTÉ DU PARC JEAN-DRAPEAU" : ["Sports, loisirs, culture et développement social"],
    }

    SERVICE_AGGREGATOR = {
        "AHUNTSIC-CARTIERVILLE" : "ARRONDISSEMENT D'AHUNTSIC-CARTIERVILLE",
        "ANJOU" : "ARRONDISSEMENT D'ANJOU",
        "ARRONDISSEMENT DE CÔTE-DES-NEIGES-NOTRE-DAME-DE-GRÂCE" : "ARRONDISSEMENT DE CÔTE-DES-NEIGES - NOTRE-DAME-DE-GRÂCE",
        "CÔTE-DES-NEIGES–NOTRE-DAME-DE-GRÂCE" : "ARRONDISSEMENT DE CÔTE-DES-NEIGES - NOTRE-DAME-DE-GRÂCE",
        "ARRONDISSEMENT DE RIVIÈRE-DES-PRAIRIES-POINTE-AUX-TREMBLES" : "ARRONDISSEMENT DE RIVIÈRE-DES-PRAIRIES–POINTE-AUX-TREMBLES",
        "RIVIÈRE-DES-PRAIRIES–POINTE-AUX-TREMBLES" : "ARRONDISSEMENT DE RIVIÈRE-DES-PRAIRIES–POINTE-AUX-TREMBLES",
        "ARRONDISSEMENT LE SUD-OUEST" : "ARRONDISSEMENT DU SUD-OUEST",
        "SUD-OUEST" : "ARRONDISSEMENT DU SUD-OUEST",
        "BUREAU DU VÉRIFICATEUR" : "BUREAU DU VÉRIFICATEUR GÉNÉRAL",
        "COMMISSION DES SERVICES ÉLECTRIQUES" : "COMMISSION DES SERVICES ÉLECTRIQUES DE MONTRÉAL",
        "LACHINE" : "ARRONDISSEMENT DE LACHINE",
        "LASALLE" : "ARRONDISSEMENT DE LASALLE",
        "L’ÎLE-BIZARD–STE-GENEVIÈVE" : "ARRONDISSEMENT DE L’ÎLE-BIZARD–STE-GENEVIÈVE",
        "MERCIER–HOCHELAGA-MAISONNEUVE" : "ARRONDISSEMENT DE MERCIER-HOCHELAGA-MAISONNEUVE",
        "MONTRÉAL-NORD" : "ARRONDISSEMENT DE MONTRÉAL-NORD",
        "OMBUDSMAN DE MONTRÉAL" : "BUREAU DE L’OMBUDSMAN",
        "OUTREMONT" : "ARRONDISSEMENT D'OUTREMONT",
        "PIERREFONDS–ROXBORO" : "ARRONDISSEMENT DE PIERREFONDS-ROXBORO",
        "PLATEAU-MONT-ROYAL" : "ARRONDISSEMENT DU PLATEAU-MONT-ROYAL",
        "ROSEMONT–LA PETITE-PATRIE" : "ARRONDISSEMENT DE ROSEMONT-LA PETITE-PATRIE",
        "SAINT-LAURENT" : "ARRONDISSEMENT DE SAINT-LAURENT",
        "SAINT-LÉONARD" : "ARRONDISSEMENT DE SAINT-LÉONARD",
        "SERVICE DE CONCERTATION DES ARRONDISSEMENTS ET DES RESSOURCES MATÉRIELLES" : "SERVICE DE LA CONCERTATION DES ARRONDISSEMENTS ET RESSOURCES MATÉRIELLES",
        "SERVICE DE LA DIVERSITÉ SOCIALE\nET DES SPORTS" : "SERVICE DE LA DIVERSITÉ SOCIALE ET DES SPORTS",
        "SERVICE DE LA GESTION ET PLANIFICATION IMMOBILIÈRE" : "SERVICE DE LA GESTION ET DE LA PLANIFICATION IMMOBILIÈRE",
        "SERVICE DE L’EAU" : "SERVICE DE L'EAU",
        "SERVICE DE POLICE" : "SERVICE DE POLICE DE LA VILLE DE MONTRÉAL",
        "SERVICE DE POLICE DE MONTRÉAL" : "SERVICE DE POLICE DE LA VILLE DE MONTRÉAL",
        "SERVICE DES AFFAIRES JURIDIQUES ET DE L’ÉVALUATION FONCIÈRE" : "SERVICE DES AFFAIRES JURIDIQUES ET DE L'ÉVALUATION FONCIÈRE",
        "SERVICES DES AFFAIRES JURIDIQUES ET DE L'ÉVALUATION FONCIÈRE" : "SERVICE DES AFFAIRES JURIDIQUES ET DE L'ÉVALUATION FONCIÈRE",
        "SERVICES DES AFFAIRES JURIDIQUES ET ÉVALUATION FONCIÈRE" : "SERVICE DES AFFAIRES JURIDIQUES ET DE L'ÉVALUATION FONCIÈRE",
        "SERVICE DE L'ESPACE POUR LA VIE" : "SERVICE DES ESPACES POUR LA VIE",
        "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT ROYAL" : "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT-ROYAL",
        "SERVICE DES GRANDS PARCS, VERDISSEMENT ET DU MONT-ROYAL" : "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT-ROYAL",
        "SERVICE DES GRANDS PARCS, VERDISSEMENT ET MONT ROYAL" : "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT-ROYAL",
        "SERVICE DES GRANDS PARCS_VERDISSEMENT ET DU MONT-ROYAL": "SERVICE DES GRANDS PARCS, DU VERDISSEMENT ET DU MONT-ROYAL",
        "SERVICE DES INFRASTRUCTURES, VOIRIE ET TRANSPORTS" : "SERVICE DES INFRASTRUCTURES, DE LA VOIRIE ET DES TRANSPORTS",
        "SERVICE DES INFRASTRUCTURES_VOIRIE ET TRANSPORTS" : "SERVICE DES INFRASTRUCTURES, DE LA VOIRIE ET DES TRANSPORTS",
        "RESSOURCES HUMAINES" : "SERVICE DES RESSOURCES HUMAINES",
        "SERVICE DES TECHNOLOGIES DE L’INFORMATION" : "SERVICE DES TECHNOLOGIES DE L'INFORMATION",
        "SERVICES DES TECHNOLOGIES DE L'INFORMATION" : "SERVICE DES TECHNOLOGIES DE L'INFORMATION",
        "SERVICE DU MATERIEL ROULANT ET ATELIERS" : "SERVICE DU MATÉRIEL ROULANT ET DES ATELIERS",
        "SERVICE DU MATÉRIEL ROULANT ET DES ATELIER" : "SERVICE DU MATÉRIEL ROULANT ET DES ATELIERS",
        "VERDUN" : "ARRONDISSEMENT DE VERDUN",
        "VILLE-MARIE" : "ARRONDISSEMENT DE VILLE-MARIE",
        "VILLERAY–ST-MICHEL–PARC-EXTENSION" : "ARRONDISSEMENT DE VILLERAY-SAINT-MICHEL-PARC-EXTENSION",
        "SERVICE DE DÉVELOPPEMENT ÉCONOMIQUE" : "SERVICE DU DÉVELOPPEMENT ÉCONOMIQUE",
        "SERVICE MISE EN VALEUR DU TERRITOIRE" : "SERVICE DE LA MISE EN VALEUR DU TERRITOIRE",
        "FACTURATION PÉRIODIQUE À RÉPARTIR SELION UTILISATION" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "FACTURATION PÉRIODIQUE À RÉPARTIR SELON CONSOMMATION" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "FACTURATION PÉRIODIQUE À RÉPARTIR SELON UTILISATEURS" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "FACTURATION PÉRIODIQUE À RÉPARTIR SELON UTILISATION" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "FACTURATION PÉRIODIQUE À RÉPARTIR SELON UTILISATON" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "FACTURÉ SELON SITE" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "À REDISTRIBUER SELON UTILISATEURS" : "FACTURATION PÉRIODIQUE À RÉPARTIR",
        "SERA RÉPARTI ENTRE LES UTILISATEURS" : "FACTURATION PÉRIODIQUE À RÉPARTIR"

    }


class ProductionConfig(Config):
    DEBUG = False
    SENDMAIL = True

    ADMINS = ['stephane@opennorth.ca']

class StagingConfig(Config):
    URL_ROOT = 'https://ovc-stage.herokuapp.com'
    SENDMAIL = True
    DEVELOPMENT = False
    DEBUG = False

class DevelopmentConfig(Config):
    URL_ROOT = 'http://localhost:5000'
    DEVELOPMENT = True
    DEBUG = True
    

class TestingConfig(Config):
    TESTING = True
    SUPPLIER_SIZE = [0, 100000, 10000000]

    DATA_SOURCES = [
        {
            'name': 'Conseil Municipal',
            'mapper': 'field_mapper_pol_mtl',
            'url': 'fixtures/contracts.csv',
            'type': 'contract'
        },
         {
            'name': 'Conseil Municipal',
            'mapper': 'field_mapper_subvention_mtl',
            'url': 'fixtures/subventions.csv',
            'type': 'subvention'
        },       
    ]
