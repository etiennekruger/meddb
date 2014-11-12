import logging
import json

LANGUAGES = {
    'en': u'English',
    'fr': u'Français',
    'pt': u'Português',
}

HOST = 'http://med-db.medicines.localhost:5000/'
API_HOST = 'http://med-db-api.medicines.localhost:5001/'
SERVER_NAME = 'medicines.localhost:5000'

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://med_db:med_db@localhost/med_db'
SQLALCHEMY_ECHO = True

RESULTS_PER_PAGE = 50

ADMIN_USER = "admin@code4sa.org"

MAX_AGE = 365
