import logging

HOST = 'http://med-db.khutjo.demo4sa.org/'
API_HOST = 'http://med-db-api.khutjo.demo4sa.org/'
SERVER_NAME = 'khutjo.demo4sa.org'

LOG_LEVEL = logging.DEBUG
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:////var/www/med-db/instance/med-db.db'

RESULTS_PER_PAGE = 100

ADMIN_USER = "admin@code4sa.org"

MAX_AGE = 365