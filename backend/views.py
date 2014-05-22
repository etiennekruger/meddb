from backend import logger, app, db
import models
import flask
import json
import serializers
from flask.ext import login
from sqlalchemy import func, or_
import datetime
import events
import cache

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

# -------------------------------------------------------------------
# Expensive functions, that only needs to be run from time to time:
#

def calculate_db_overview():
    """
    Run a set of queries to get an overview of the database.
    THIS IS COMPUTATIONALLY EXPENSIVE
    """


    logger.debug("Calculating DB overview")
    overview = {}

    # number of products being tracked
    count_products = db.session.query(
        func.count(models.Product.product_id)
    ).scalar()
    overview['count_products'] = count_products

    # number of distinct medicines
    count_medicines = db.session.query(
        func.count(models.Medicine.medicine_id)
    ).scalar()
    overview['count_medicines'] = count_medicines

    # number of recent procurements
    # i.e. they have start or end dates after the cutoff
    cutoff = datetime.datetime.today() - datetime.timedelta(days=365)
    count_recent_procurements = db.session.query(
        func.count(models.Procurement.procurement_id)) \
        .filter(
        or_(
            models.Procurement.start_date > cutoff,
            models.Procurement.end_date > cutoff
        )
    ).scalar()
    overview['count_recent_procurements'] = count_recent_procurements

    # number of recent procurements logged per country
    top_sources = []
    sources = db.session.query(models.Procurement.country_id,
                               func.count(models.Procurement.procurement_id)) \
        .filter(
        or_(
            models.Procurement.start_date > cutoff,
            models.Procurement.end_date > cutoff
        )
    ) \
        .group_by(models.Procurement.country_id) \
        .order_by(func.count(models.Procurement.procurement_id).desc()).all()

    for country_id, count in sources[0:5]:
        print 'Country ID %d: %d' % (country_id, count)
        country = models.Country.query.get(country_id)
        top_sources.append(
            {
                'country': country.to_dict(),
                'procurement_count': count
            }
        )
    overview['top_sources'] = top_sources
    return overview


def calculate_autocomplete():
    """
    Retrieve all product records and serialize them for use by the autocomplete endpoint.
    THIS IS COMPUTATIONALLY EXPENSIVE
    """

    logger.debug("Calculating autocomplete")
    products = models.Product.query.all()
    out = []
    for product in products:
        out.append(product.to_dict())
    return out

# -------------------------------------------------------------------
# API endpoints:
#

@app.route('/overview/')
def overview():
    """
    Give a broad overview of the size of -, and recent activity related to, the database.
    """

    tmp = cache.retrieve('db_overview')
    if tmp:
        logger.debug("DB overview served from cache")
        return send_api_response(tmp)
    else:
        tmp = calculate_db_overview()
        cache.store('db_overview', json.dumps(tmp, cls=serializers.CustomEncoder))
        return send_api_response(json.dumps(tmp))


api_resources = {
    'medicine': (models.Medicine, models.Medicine.medicine_id),
    'product': (models.Product, models.Product.product_id),
    'procurement': (models.Procurement, models.Procurement.procurement_id),
    'manufacturer': (models.Manufacturer, models.Manufacturer.manufacturer_id),
    'supplier': (models.Supplier, models.Supplier.supplier_id),
    }

@app.route('/')
def index():
    """
    Landing page. Return links to available endpoints.
    """

    endpoints = {}
    for resource in api_resources.keys():
        endpoints[resource] = API_HOST + resource + "/"
    return send_api_response(json.dumps(endpoints))


@app.route('/<string:resource>/')
@app.route('/<string:resource>/<int:resource_id>/')
def resource(resource, resource_id=None):
    """
    Generic endpoint for resources. If an ID is specified, a single record is returned,
    otherwise a list of records is returned.
    """

    if not api_resources.get(resource):
        raise ApiException(400, "The specified resource type does not exist.")

    model = api_resources[resource][0]
    model_id = api_resources[resource][1]
    include_related = False
    count, next = None, None
    if resource_id:
        include_related = True
        queryset = model.query.filter(model_id==resource_id).first()
        if queryset is None:
            raise ApiException(404, "Could not find the " + resource.upper() + " that you were looking for.")
    else:
        # validate paging parameters
        page = 0
        per_page = app.config['RESULTS_PER_PAGE']
        if flask.request.args.get('page'):
            try:
                page = int(flask.request.args.get('page'))
            except ValueError:
                raise ApiException(422, "Please specify a valid 'page'.")
        queryset = model.query.limit(per_page).offset(page*per_page).all()
        count = model.query.count()
        next = None
        if count > (page + 1) * per_page:
            next = flask.request.url_root + resource + "/?page=" + str(page+1)
    out = serializers.queryset_to_json(queryset, count=count, next=next, include_related=include_related)
    return send_api_response(out)


@app.route('/autocomplete/<query>/')
def autocomplete(query):
    """
    Return the name and product_id of each product that matches the given query, together with the name and
    country of the manufacturer.
    """

    out = []
    product_list_json = cache.retrieve('product_list')
    if product_list_json:
        logger.debug('calculating autocomplete from cache')
        product_list = json.loads(product_list_json)
    else:
        product_list = calculate_autocomplete()
        cache.store('product_list', json.dumps(product_list, cls=serializers.CustomEncoder))
    i = 0
    for product in product_list:
        tmp = {}
        product_name = product['name'].lower()
        medicine_name = ""
        if product.get('medicine'):
            medicine_name = product['medicine']['name'].lower()
        if i < 10 and (query in product_name or query in medicine_name):
            i += 1
            tmp['product_id'] = product['product_id']
            tmp['name'] = product['name']
            if product['manufacturer']:
                tmp['manufacturer'] = {}
                tmp['manufacturer']['name'] = product['manufacturer']['name']
                if product['manufacturer']['country']:
                    tmp['manufacturer']['country'] = product['manufacturer']['country']
            out.append(tmp)
    return send_api_response(json.dumps(out))


@app.route('/recent_updates/')
def recent_updates():
    """
    Return a list of purchases that have recently been added
    """

    procurements = models.Procurement.query.order_by(models.Procurement.added_on.desc()).limit(20).all()
    return serializers.queryset_to_json(procurements)