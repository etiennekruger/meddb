from backend import logger, app, db
import models
from models import *
import flask
from flask import g, request, abort, redirect, url_for, session, make_response
from functools import wraps
import json
import serializers
from sqlalchemy import func, or_, distinct
import datetime
import cache
from operator import itemgetter
import re
from xlsx import XLSXBuilder

API_HOST = app.config["API_HOST"]
MAX_AGE = app.config["MAX_AGE"]

api_resources = {
    'medicine': (Medicine, Medicine.medicine_id),
    'product': (Product, Product.product_id),
    'procurement': (Procurement, Procurement.procurement_id),
    'manufacturer': (Manufacturer, Manufacturer.manufacturer_id),
    'supplier': (Supplier, Supplier.supplier_id),
    }

available_countries = {
    "AGO":  "Angola",
    "BWA":  "Botswana",
    "COD":  "Congo (DRC)",
    "LSO":  "Lesotho",
    "MWI":  "Malawi",
    "MUS":  "Mauritius",
    "MOZ":  "Mozambique",
    "NAM":  "Namibia",
    "SYC":  "Seychelles",
    "ZAF":  "South Africa",
    "SWZ":  "Swaziland",
    "TZA":  "Tanzania",
    "ZMB":  "Zambia",
    }

# handling static files (only relevant during development)
app.static_folder = 'static'
app.add_url_rule('/static/<path:filename>',
                 endpoint='static',
                 view_func=app.send_static_file,
                 subdomain='api-med-db')


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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or not g.user.is_active():
            raise ApiException(401, "You need to be logged-in in order to access this resource.")
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def load_user():

    user = None
    # handle authentication via Auth Header
    if request.headers.get('Authorization') and request.headers['Authorization'].split(":")[0]=="ApiKey":
        key_value = request.headers['Authorization'].split(":")[1]
        api_key = ApiKey.query.filter_by(key=key_value).first()
        if api_key:
            user = api_key.user
    # handle authentication via session cookie (for admin)
    if session and session.get('api_key'):
        api_key = ApiKey.query.filter_by(key=session.get('api_key')).first()
        if api_key:
            user = api_key.user
    g.user = user
    return


# -------------------------------------------------------------------
# Expensive functions, that only needs to be run from time to time:
#

def calculate_db_overview():
    """
    Run a set of queries to get an overview of the database.
    THIS IS COMPUTATIONALLY EXPENSIVE
    """

    cutoff = datetime.datetime.today() - datetime.timedelta(days=MAX_AGE)

    logger.debug("Calculating DB overview")
    overview = {}

    # number of recent products & medicines
    count_procurements, count_products, count_medicines = Procurement.query.join(Product).filter(
        or_(
            Procurement.start_date > cutoff,
            Procurement.end_date > cutoff
        )
    ).filter(
        Procurement.approved != False
    ).with_entities(
        func.count(Procurement.procurement_id),
        func.count(distinct(Procurement.product_id)),
        func.count(distinct(Product.medicine_id))
    ).first()
    overview['count_procurements'] = count_procurements
    overview['count_products'] = count_products
    overview['count_medicines'] = count_medicines

    # number of recent procurements logged per country
    top_sources = []
    sources = db.session.query(Procurement.country_id,
                               func.count(Procurement.procurement_id)) \
        .filter(
        or_(
            Procurement.start_date > cutoff,
            Procurement.end_date > cutoff
        )
    ).filter(
        Procurement.approved != False
    ).group_by(Procurement.country_id) \
        .order_by(func.count(Procurement.procurement_id).desc()).all()

    for country_id, count in sources[0:5]:
        print 'Country ID %d: %d' % (country_id, count)
        country = Country.query.get(country_id)
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
    Retrieve all medicine records and serialize them for use by the autocomplete endpoint.
    THIS IS slightly COMPUTATIONALLY EXPENSIVE
    """

    logger.debug("Calculating autocomplete")
    medicines = Medicine.query.order_by(Medicine.name).all()
    out = []
    for medicine in medicines:
        tmp_dict = {
            'name': medicine.name,
            'medicine_id': medicine.medicine_id,
            }
        out.append(tmp_dict)
    return out


def calculate_country_overview(country):
    """
    THIS IS COMPUTATIONALLY EXPENSIVE
    """

    logger.debug("Calculating country overview")

    # iterate through all medicines in the db
    medicines = Medicine.query.order_by(Medicine.name).all()
    medicines_out = []
    for medicine in medicines:
        tmp = {
            'score': 0,
            'overall_spend': 0,
            'potential_savings': 0,
            }
        # serialize medicine, so that procurements may be ordered
        medicine_dict = medicine.to_dict(include_related=True)
        procurements = medicine_dict['procurements']
        if not procurements:
            continue
        # calculate the total spend and potential savings for each transaction
        best_price = procurements[0]['unit_price_usd']
        for procurement in procurements:
            if procurement['country']['code']==country.code:
                total = procurement['quantity'] * procurement['pack_price_usd']
                tmp_diff = procurement['unit_price_usd'] - best_price
                potential_saving = procurement['quantity'] * procurement['pack_size'] * tmp_diff
                tmp['overall_spend'] += total
                tmp['potential_savings'] += potential_saving
        if tmp['overall_spend']:
            tmp['name'] = medicine.name
            tmp['medicine_id'] = medicine.medicine_id
            tmp['score'] = 1 - (tmp['potential_savings']/float(tmp['overall_spend']))
            medicines_out.append(tmp)

    # score medicines by how close their spend is to the theoretical best
    medicines_out = sorted(medicines_out, key=itemgetter("potential_savings"))
    medicines_out.reverse()
    return medicines_out


def calculate_country_rankings():
    """
    THIS IS COMPUTATIONALLY EXPENSIVE
    """

    logger.debug("Calculating country rankings")

    ranking = {}
    for country_code in available_countries.keys():
        ranking[country_code] = {
            'score': 0,
            'overall_spend': 0,
            'potential_savings': 0,
            }
    # iterate through all medicines in the db
    medicines = Medicine.query.order_by(Medicine.name).all()
    for medicine in medicines:
        # serialize medicine, so that procurements may be ordered
        medicine_dict = medicine.to_dict(include_related=True)
        procurements = medicine_dict['procurements']
        if not procurements:
            continue
        # calculate the total spend and potential savings for each transaction
        best_price = procurements[0]['unit_price_usd']
        for procurement in procurements:
            if ranking.get(procurement['country']['code']):
                total = procurement['quantity'] * procurement['pack_price_usd']
                tmp_diff = procurement['unit_price_usd'] - best_price
                potential_saving = procurement['quantity'] * procurement['pack_size'] * tmp_diff
                ranking[procurement['country']['code']]['overall_spend'] += total
                ranking[procurement['country']['code']]['potential_savings'] += potential_saving
    # score countries by how close their spend is to the theoretical best
    ranked_list = []
    for country_code, entry in ranking.iteritems():
        if entry['overall_spend']:
            entry['score'] = 1 - (entry['potential_savings']/float(entry['overall_spend']))
        entry['country'] = Country.query.filter_by(code=country_code).one().to_dict()
        ranked_list.append(entry)
    ranked_list = sorted(ranked_list, key=itemgetter("score"))
    ranked_list.reverse()
    out = {'count': len(ranked_list), 'countries': ranked_list}
    return out

# -------------------------------------------------------------------
# API endpoints:
#

@app.route('/login/', subdomain='med-db-api', methods=['POST',])
def login():

    email = request.json.get('email')
    password = request.json.get('password')

    # find user in database
    user = User.query.filter_by(email=email).first()

    if user is not None and user.verify_password(password):
        # find api key
        api_key = ApiKey.query.filter_by(user_id=user.user_id).first()
        if not api_key:
            api_key = ApiKey(user=user)
            db.session.add(api_key)
        # re-generate key
        api_key.generate_key()
        # return user & api key details
        db.session.commit()
        out = user.to_dict()
        out['api_key'] = api_key.key
        return send_api_response(json.dumps(out))
    else:
        raise ApiException(400, "The email address or password is incorrect.")


@app.route('/register/', subdomain='med-db-api', methods=['POST',])
def register():

    email = request.json.get('email')
    password = request.json.get('password')

    # validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ApiException(400, "Please supply a valid email address.")
    if email is None or password is None:
        raise ApiException(400, "Missing arguments. Specify both 'email' and 'password'.")
    if User.query.filter_by(email=email).first() is not None:
        raise ApiException(400, "This user already exists.")

    # create new user
    user = User(email=email)
    user.hash_password(password)
    db.session.add(user)
    # create an api key for this user
    api_key = ApiKey(user=user)
    api_key.generate_key()
    db.session.add(api_key)
    db.session.commit()
    out = user.to_dict()
    out['api_key'] = api_key.key

    return send_api_response(json.dumps(out))


@app.route('/user/<int:user_id>/', subdomain='med-db-api')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ApiException(404, "The specified User record doesn't exist.")
    return send_api_response(json.dumps(user.to_dict()))


@app.route('/overview/', subdomain='med-db-api')
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


@app.route('/', subdomain='med-db-api')
def index():
    """
    Landing page. Return links to available endpoints.
    """

    endpoints = {}
    for resource in api_resources.keys():
        endpoints[resource] = API_HOST + resource + "/"
    return send_api_response(json.dumps(endpoints))


@app.route('/<string:resource>/', subdomain='med-db-api')
@app.route('/<string:resource>/<int:resource_id>/', subdomain='med-db-api')
def resource(resource, resource_id=None):
    """
    Generic endpoint for resources. If an ID is specified, a single record is returned,
    otherwise a list of records is returned.
    """

    if not api_resources.get(resource):
        raise ApiException(400, "The specified resource type does not exist.")

    if resource == "procurement":
        if g.user is None or not g.user.is_active():
            raise ApiException(401, "You need to be logged-in in order to access this resource.")

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


@app.route('/autocomplete/<query>/', subdomain='med-db-api')
def autocomplete(query):
    """
    Return the name and medicine_id of each medicine that matches the given query.
    """

    out = []
    medicine_list_json = cache.retrieve('medicine_list')
    if medicine_list_json:
        logger.debug('calculating autocomplete from cache')
        medicine_list = json.loads(medicine_list_json)
    else:
        medicine_list = calculate_autocomplete()
        cache.store('medicine_list', json.dumps(medicine_list, cls=serializers.CustomEncoder))
    for medicine in medicine_list:
        tmp = {}
        query_index = medicine['name'].lower().find(query.lower())
        if query_index > -1:
            tmp['medicine_id'] = medicine['medicine_id']
            tmp['name'] = medicine['name']
            tmp['index'] = query_index
            out.append(tmp)
        if len(out) > 20:
            break
    out = sorted(out, key=itemgetter('index'))
    if len(out) > 10:
        out = out[0:10]
    return send_api_response(json.dumps(out))


@app.route('/recent_updates/', subdomain='med-db-api')
def recent_updates():
    """
    Return a list of purchases that have recently been added
    """

    procurements = Procurement.query.order_by(Procurement.added_on.desc()).limit(20).all()
    return serializers.queryset_to_json(procurements)


@app.route('/country_report/<string:country_code>/', subdomain='med-db-api')
def country_report(country_code):
    """
    """

    country_code = country_code.upper()
    if not available_countries.get(country_code):
        raise ApiException(400, "Reports are not available for the country that you specified.")

    country = Country.query.filter_by(code=country_code).one()

    report_json = cache.retrieve('country_overview_' + country.code)
    if report_json:
        logger.debug('loading country overview from cache')
    else:
        report = {}
        procurement_list = []
        procurements = Procurement.query.filter_by(country=country).filter_by(approved=True).order_by(Procurement.start_date.desc(), Procurement.end_date.desc()).all()
        for procurement in procurements:
            procurement_list.append(procurement.to_dict(include_related=True))
        report['country'] = country.to_dict()
        report['medicines'] = calculate_country_overview(country)
        report['procurements'] = procurement_list
        report_json = json.dumps(report, cls=serializers.CustomEncoder)
        cache.store('country_overview_' + country.code, report_json)

    return send_api_response(report_json)


@app.route('/country_ranking/', subdomain='med-db-api')
def country_ranking():
    """
    """

    ranking_json = cache.retrieve('country_ranking')
    if ranking_json:
        logger.debug('loading country ranking from cache')
    else:
        ranking = calculate_country_rankings()
        ranking_json = json.dumps(ranking)
        cache.store('country_ranking', ranking_json)
    return send_api_response(ranking_json)


@app.route('/active_medicines/', subdomain='med-db-api')
def active_medicines():
    """
    Return a list of medicines for which we have recent procurement records.
    """

    cutoff = datetime.datetime.today() - datetime.timedelta(days=MAX_AGE)

    tmp = db.session.query(Medicine.medicine_id, Medicine.name, func.count(Procurement.procurement_id)) \
        .join(Medicine.products) \
        .join(Product.procurements) \
        .filter(
        or_(
            Procurement.start_date > cutoff,
            Procurement.end_date > cutoff
        )
    ) \
        .group_by(Medicine.medicine_id) \
        .having(func.count(Procurement.procurement_id) > 0) \
        .all()
    result = [{"medicine_id": medicine_id, "name": name, "procurement_count": count} for medicine_id, name, count in tmp]
    out = {"next": None, "result": result}
    out = json.dumps(out)
    return send_api_response(out)


@app.route('/xlsx/<string:country_code>/', subdomain='med-db-api')
def download_procurements(country_code):

    country_code = country_code.upper()
    if not available_countries.get(country_code):
        raise ApiException(400, "Reports are not available for the country that you specified.")

    country = Country.query.filter_by(code=country_code).one()

    procurements = Procurement.query.filter_by(country=country).filter_by(approved=True).order_by(Procurement.start_date.desc(), Procurement.end_date.desc()).all()
    out = XLSXBuilder(procurements)
    xlsx = out.build()
    resp = make_response(xlsx)
    resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    filename = "procurements-" + country.name.lower().replace(" ", "_") + ".xlsx"
    resp.headers['Content-Disposition'] = "attachment;filename=" + filename
    return resp
