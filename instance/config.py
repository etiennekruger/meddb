import logging
import json

HOST = 'http://med-db.medicines.localhost:5000/'
API_HOST = 'http://med-db-api.medicines.localhost:5001/'
SERVER_NAME = 'medicines.localhost:5000'

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/petrus/Desktop/code4sa/med-db/instance/med-db.db'
# SQLALCHEMY_ECHO = True

RESULTS_PER_PAGE = 20

ADMIN_USER = "admin@code4sa.org"