from backend import logger, app, db
import models
import flask
import json
import serializers

API_HOST = app.config["API_HOST"]


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


def send_api_response(data_json):

    response = flask.make_response(data_json)
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Content-Type'] = "application/json"
    return response


@app.route('/')
def index():
    """
    Landing page. Return links to available endpoints.
    """

    endpoints = {
        "medicines": API_HOST + "medicine/",
        "medicines/<id>/": API_HOST + "medicine/1/"
    }
    return send_api_response(json.dumps(endpoints))


@app.route('/medicine/')
@app.route('/medicine/<int:medicine_id>/')
def medicine(medicine_id=None):
    """
    """

    if medicine_id:
        queryset = models.Medicine.query.filter(models.Medicine.medicine_id==medicine_id).first()
        if queryset is None:
            raise ApiException(404, "Could not find the Medicine that you were looking for.")
    else:
        queryset = models.Medicine.query.all()
    out = serializers.queryset_to_json(queryset)
    return send_api_response(out)