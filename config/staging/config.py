import logging

HOST = 'http://med-db.medicines.demo4sa.org/'
API_HOST = 'http://med-db-api.medicines.demo4sa.org/'
SERVER_NAME = 'medicines.demo4sa.org'

LANGUAGES = {
    'en': u'English',
    'fr': u'Français',
    'pt': u'Português',
}

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = False

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://med_db:med_db@localhost/med_db'

RESULTS_PER_PAGE = 50

ADMIN_USER = "admin@code4sa.org"

MAX_AGE = 365