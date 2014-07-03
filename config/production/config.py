import logging

HOST = 'http://med-db.medicines.sadc.int/'
API_HOST = 'http://med-db.medicines.sadc.int/'

LOG_LEVEL = logging.INFO
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = False

SQLALCHEMY_DATABASE_URI = 'sqlite:////var/www/med-db/instance/med-db.db'

RESULTS_PER_PAGE = 50

ADMIN_USER = "admin@code4sa.org"