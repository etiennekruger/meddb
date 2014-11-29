import logging
from logging.handlers import RotatingFileHandler
import sys, os
import flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('backend', instance_relative_config=True, static_folder=None)
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


class ApiException(Exception):
    """
    Class for handling all of our expected API errors.
    """

    def __init__(self, status_code, message):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {
            "code": self.status_code,
            "message": self.message
        }
        return rv


@app.errorhandler(ApiException)
def handle_api_exception(error):
    """
    Error handler, used by flask to pass the error on to the user, rather than catching it and throwing a HTTP 500.
    """

    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.errorhandler(Exception)
def log_exception(e):
    """
    Log all uncaught exceptions.
    """
    logger.exception(e)
    raise

import admin
import views