import logging
import json

HOST = 'http://127.0.0.1:5000/'
API_HOST = 'http://127.0.0.1:5001/'

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/petrus/Desktop/code4sa/med-db/instance/med-db.db'
SQLALCHEMY_ECHO = True

RESULTS_PER_PAGE = 50

ADMIN_USER = "admin@code4sa.org"