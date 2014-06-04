import logging
from logging.handlers import RotatingFileHandler
import sys, os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('med-db_backend', instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)
app.config.from_pyfile('config_private.py', silent=True)

db = SQLAlchemy(app)

# load log level from config
LOG_LEVEL = app.config['LOG_LEVEL']
LOGGER_NAME = app.config['LOGGER_NAME']

# create logger for this application
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)

# declare format for logging to file
file_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s [backend]: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
)

# add file handler
log_path = app.instance_path[0:app.instance_path.index('instance')]
file_handler = RotatingFileHandler(os.path.join(log_path, 'debug.log'))
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# also log to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(LOG_LEVEL)
stream_handler.setFormatter(file_formatter)
logger.addHandler(stream_handler)

import views
import admin