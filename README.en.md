[![Build Status](https://travis-ci.org/opennorth/ovc-vdm.svg?branch=master)](https://travis-ci.org/opennorth/ovc-vdm)

Other languages: [Français](README.md)

# A tool for visualising contracts for the City of Montreal

Consolidates files contracts and grants from the City of Montreal hosted on [the open data portal](http://donnees.ville.montreal.qc.ca/) to produce:

- A programmable interface (API) according to the [Contracting Open Data Standard](http://standard.open-contracting.org/latest/en/) format and to sort the data according to different parameters
- Data visualization for listing and exporting contracts and grants. The web interface obtains the data by connecting to the API.

## Dependencies

The API requires the following:

- Python 2.7 or greater
- Postgresql 9.3 or greater

The code was developed using the [Flask] (http://flask.pocoo.org/) Python microframework. Flask and all other necessary libraries are contained in the file `requirements.txt`.

The project follows standards for hosting on [Heroku](https://heroku.com). That said, it is possible to execute the code on any configuration meeting the above prerequisites; it will be necessary to add a WSGI as [uwsgi] (http://flask.pocoo.org/docs/0.10/deploying/uwsgi/) to link the python code to a web server such as Apache or Nginx.

## Installation

You can clone the code using Git:

``` bash
git clone https://github.com/opennorth/ovc-vdm.git
cd ovc-vdm
```

Or [download a zip](https://github.com/opennorth/ovc-vdm/archive/master.zip).

### Installing Python dependencies

It is recommended that you setup a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for installing Python dependencies, so as to avoid effecting your wider system.

Once you've done that, install dependencies as follows.

``` bash
pip install -r requirements.txt
```

### Environment variables

You need to set the following environment variables prior to running the application:

``` bash
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DBNAME"
export EMAIL_CREDENTIALS="user@password"
```

- `APP_SETTING` sets the configuration mode for running the application. The different modes are configured in the `config.py` file.
- `DATABASE_URL` tells SQLAlchemy how to connect to the database.
- `EMAIL_CREDENTIAL` is used to generate alert emails via the platform [SendGrid](https://sendgrid.com).

### Initialize the database

Before running the application, you must setup the initial database schema as follows:

``` bash
python manage.py db init
python manage.py db upgrade
```

### Import data

There are two steps to importing the intial data into the database:

``` bash
python manage.py update_sources   # Import data sources
python manage.py update_releases  # Impore contracts and releases - takes a very long time
```

### Launch the application

``` bash
python app.py  # Run the development server
```

To use the application in production mode, it is necessary to start using [WSGI Python](http://www.fullstackpython.com/wsgi-servers.html). To run on the Heroku platform, `procfile` file is already in place.

### Run the tests

``` bash
./run_test.sh
```

This uses the [node](http://nose.readthedocs.io/en/latest/) testing library.

## Further documentation

- [API documentation](doc/api.doc.fr.md)
