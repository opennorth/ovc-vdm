[![Build Status](https://travis-ci.org/opennorth/ovc-vdm.svg?branch=master)](https://travis-ci.org/opennorth/ovc-vdm)

#Outil de visualisation des contracts (OVC) réalisé pour la Ville de Montréal

L'OVC consolide les fichiers de contrats et de subventions de la Ville de Montréal hébergés sur le portail de [données ouvertes](http://donnees.ville.montreal.qc.ca/) pour produire:

- Une interface programmable (API) conforme au format [Open Contracting Data Standard](http://standard.open-contracting.org/) et permettant de trier les données selon différents paramètres
- Une visualisation des données permettant de lister et d'exporter les contrats et subventions. L'interface web obtient les données en se connectant à l'API.

##Prérequis

L'API repose sur les technologies suivantes:
- Python 2.7 ou supérieur
- Postgresql 9.3 ou supérieur

Le code a été développé en utilisant le mini-système python [Flask](http://flask.pocoo.org/). Flask ainsi que l'ensemble des autres librairies nécessaires sont contenues dans le fichier `requirements.txt`.

Le projet a été développé en vue d'être déployé sur la plateforme [Heroku](https://heroku.com) et suit les standards suggéré pour cette plateforme. Cela étant dit, il est possible d'executer le présent code sur n'importe quelle configuration respectant les prérequis ci-dessus; il sera toutefois nécessaire d'ajouter un WSGI tel que [uWSGI](http://flask.pocoo.org/docs/0.10/deploying/uwsgi/) pour lier le code python à un serveur web comme Apache ou Nginx.

## Documentation de l'API

Le fonctionnement de l'API est documenté [ici](doc/api.doc.fr.md) 

##Installation

Il est recommandé d'executer les commandes ci-dessous à l'intérieur d'un environnement virtuel à l'aide de [virtualenv/virtualenvwrapper](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

Par exemple 

```
virtualenv /path/to/project
source /path/to/project/bin/activate
```

###Installer le code et les librairies

Cloner le présent dépôt et installer les librairies requises:

```
git clone https://github.com/opennorth/ovc-vdm.git
cd ovc-vdm
pip install -r requirements.txt
```

###Variables d'environnement

Positionner les variables d'environnement, par exemple dans le script de postactivate de virtualenvwrapper.
Les variables à positionner sont les suivantes:

```
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgresql://host/dbname"
export EMAIL_CREDENTIALS="user@password"
```

`APP_SETTING` spécifie si l'application fonctionne en mode développement ou test (mode 'debug' activé) ou préproduction ou production (mode 'debug' désactivé). Les différents modes sont configurés dans le fichier `config.py`.

`EMAIL_CREDENTIAL` est utilisé pour générer des courriels d'alerte via la plateforme [SendGrid](https://sendgrid.com).

###Initialiser la base de données

```
python manage.py db init
python manage.py db upgrade
```

Maintenant la base de données contient les tables nécessaires pour fonctionner.


###Remplir les tables

```
python manage.py update_sources
python manage.py update_releases
```

La première commande insère dans la base de données les sources de données tandis que la seconde récupère les fichiers et insère les contrats/releases dans la base de données. La seconde étape peut prendre un certain temps (une trentaine de minutes).

###Lancer l'application

Pour lancer l'application en mode développement, il suffit d'utiliser la commande suivntes:

```
python app.py
```

Pour utiliser l'application en mode production, il est nécessaire de la lancer en utilisant un [WSGI Python](http://www.fullstackpython.com/wsgi-servers.html). Pour fonctionner sur la plateforme Heroku, le fichier `procfile` est déjà en place.


###Executer les tests

L'application utilise `nose` réaliser des tests unitaires:

```
./run_test.sh
```

