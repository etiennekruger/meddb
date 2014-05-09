import logging
import json

API_HOST = 'http://127.0.0.1:5000/'

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/med-db.db'

RESULTS_PER_PAGE = 50