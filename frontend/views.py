from flask import render_template, flash, redirect, request, url_for, session
from frontend import app, logger
import requests
from requests import ConnectionError
import operator
import dateutil.parser
import forms
import json

API_HOST = app.config['API_HOST']


@app.template_filter('format_date')
def jinja2_filter_format_date(date_str):
    date = dateutil.parser.parse(date_str)
    native = date.replace(tzinfo=None)
    format='%b %Y'
    return native.strftime(format)


@app.template_filter('add_commas')
def jinja2_filter_add_commas(quantity):
    out = ""
    quantity_str = str(quantity)
    while len(quantity_str) > 3:
        tmp = quantity_str[-3::]
        out = "," + tmp + out
        quantity_str = quantity_str[0:-3]
    return quantity_str + out


def sort_list(unsorted_list, key):
    """
    Sort a list of dicts by the value found with the key provided.
    """

    return sorted(unsorted_list, key=operator.itemgetter(key))


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

    logger.debug(error)
    flash(error.message + " (" + str(error.status_code) + ")", "danger")
    if error.status_code == 401:
        return redirect(url_for('login'))
    return "OK"


def load_from_api(resource_name, resource_id=None):

    query_str = resource_name + "/"
    if resource_id:
        query_str += str(resource_id) + "/"

    headers = {}
    if session and session.get('api_key'):
        headers = {'Authorization': 'ApiKey:' + session.get('api_key')}

    try:
        response = requests.get(API_HOST + query_str, headers=headers)
        if response.status_code != 200:
            raise ApiException(response.status_code, response.json().get('message', "An unspecified error has occurred."))
        return response.json()

    except ConnectionError:
        flash('Error connecting to backend service.', 'danger')
        pass
    return


@app.route('/')
def landing():

    recent_updates = load_from_api('recent_updates')
    if recent_updates:
        recent_updates = recent_updates.get('results')

    overview = load_from_api('overview')

    return render_template(
        'index.html',
        API_HOST=API_HOST,
        active_nav_button="home",
        overview=overview,
        recent_updates=recent_updates
    )


@app.route('/medicine/<int:medicine_id>/')
def medicine(medicine_id):

    medicine = load_from_api('medicine', medicine_id)

    # sort products by average price
    max_avg_price = medicine['products'][-1]['average_price']
    max_price = medicine['procurements'][-1]['unit_price_usd']

    # find the best procurements
    best_procurements = medicine['procurements']
    if len(best_procurements) > 5:
        best_procurements = best_procurements[0:5]

    # calculate potential cost difference
    form_args = []
    if request.args.get("compare-quantity") and request.args.get("compare-price"):
        form_args = request.args
        try:
            compare_quantity = int(form_args['compare-quantity'])
            compare_price = float(form_args['compare-price'])
            total_expected = compare_price * compare_quantity

            for procurement in best_procurements:
                unit_price = float(procurement['unit_price_usd'])
                procurement['cost_difference'] = (unit_price - compare_price) * compare_quantity
        except Exception as e:
            flash("There was a problem with your input.", "warning")
            logger.debug(e)
            pass

    return render_template(
        'medicine.html',
        API_HOST=API_HOST,
        medicine=medicine,
        active_nav_button="medicines",
        max_price = max_price,
        max_avg_price = max_avg_price,
        best_procurements = best_procurements,
        form_args = form_args,
    )

@app.route('/procurement/<int:procurement_id>/')
def procurement(procurement_id):

    procurement = load_from_api('procurement', procurement_id)
    return render_template(
        'procurement.html',
        API_HOST=API_HOST,
        procurement=procurement,
        active_nav_button="procurement"
    )

@app.route('/login/', methods=['GET', 'POST'])
def login():

    login_form = forms.LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        data = json.dumps(request.form)
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(API_HOST + 'login/', data=data, headers=headers)
            if response.status_code != 200:
                raise ApiException(response.status_code, response.json().get('message', "An unspecified error has occurred."))
            user_dict = response.json()
            api_key = user_dict.get('api_key')
            email = user_dict.get('email')
            session['api_key'] = api_key
            session['email'] = email
            return redirect(url_for('landing'))
        except ConnectionError:
            flash('Error connecting to backend service.', 'danger')
            pass

    return render_template(
        'login.html',
        form=login_form
    )

@app.route('/logout/', methods=['GET', 'POST'])
def logout():

    session.clear()
    return redirect(url_for('landing'))

@app.route('/register/', methods=['GET', 'POST'])
def register():

    register_form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and register_form.validate():
        data = json.dumps(request.form)
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(API_HOST + 'register/', data=data, headers=headers)
            if response.status_code != 200:
                raise ApiException(response.status_code, response.json().get('message', "An unspecified error has occurred."))
            user_dict = response.json()
            api_key = user_dict.get('api_key')
            email = user_dict.get('email')
            session['api_key'] = api_key
            session['email'] = email
            return redirect(url_for('landing'))
        except ConnectionError:
            flash('Error connecting to backend service.', 'danger')
            pass

    return render_template(
        'register.html',
        form=register_form
    )

@app.route('/admin/')
def admin_redirect():
    return redirect(API_HOST + "admin/")


@app.route('/meddb/')
def legacy_redirect():
    return redirect("/", 301)