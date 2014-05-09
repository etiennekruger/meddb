from flask import render_template
from frontend import app
import requests
import dateutil.parser
import operator

api_host = app.config['API_HOST']


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

    response = requests.get(api_host + 'product/' + str(product_id) + "/")
    product = response.json()
    return render_template('product.html', product=product, active_nav_button="medicines")

@app.route('/supplier/<supplier_id>/')
def supplier(supplier_id):

    response = requests.get(api_host + 'supplier/' + str(supplier_id) + "/")
    supplier = response.json()
    return render_template('supplier.html', supplier=supplier, active_nav_button="suppliers")