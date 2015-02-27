DATABASE_URL="postgresql://localhost/ovc_test" APP_SETTINGS="config.TestingConfig" PGDATABASE="ovc_test" nosetests --with-coverage --cover-package=app,models,manage,mapper
