from flask import render_template
from frontend import app
import requests
import operator
import dateutil

API_HOST = app.config['API_HOST']


@app.template_filter('format_date')
def jinja2_filter_format_date(date_str):
    date = dateutil.parser.parse(date_str)
    native = date.replace(tzinfo=None)
    format='%b %Y'
    return native.strftime(format)


def sort_list(unsorted_list, key):
    """
    Sort a list of dicts by the value found with the key provided.
    """

    return sorted(unsorted_list, key=operator.itemgetter(key))


@app.route('/')
def landing():

    return render_template('index.html', active_nav_button="home")

@app.route('/product/<product_id>/')
def product(product_id):

    response = requests.get(API_HOST + 'product/' + str(product_id) + "/")
    product = response.json()
    return render_template('product.html', product=product, active_nav_button="medicines")

@app.route('/supplier/<supplier_id>/')
def supplier(supplier_id):

    response = requests.get(API_HOST + 'supplier/' + str(supplier_id) + "/")
    supplier = response.json()
    return render_template('supplier.html', supplier=supplier, active_nav_button="suppliers")