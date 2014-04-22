import logging
import json

API_HOST = 'http://127.0.0.1:8000/json/'

LOG_LEVEL = logging.INFO
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = True
