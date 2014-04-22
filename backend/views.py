from backend import logger, app, db
import models
import flask


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


def send_api_response(data_dict):

    response = flask.jsonify(data_dict)
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route('/')
def index():
    """
    Landing page. Return links to available endpoints.
    """

    out = {"hello": "world"}
    return send_api_response(out)