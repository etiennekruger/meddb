import logging

API_HOST = 'http://medicines.sadc.int/meddb/json/'

LOG_LEVEL = logging.INFO
LOGGER_NAME = "med-db-logger"  # make sure this is not the same as the name of the package to avoid conflicts with Flask's own logger
DEBUG = False