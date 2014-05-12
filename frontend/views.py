from flask import render_template, flash
from frontend import app
import requests
import operator
import dateutil
import datetime

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

    top_sources = [
        {"name": "Zambia", "contribution_count": 154},
        {"name": "South Africa", "contribution_count": 98},
        {"name": "Botswana", "contribution_count": 54},
        {"name": "Malawi", "contribution_count": 34},
        {"name": "Seychelles", "contribution_count": 20}
    ]

    recent_products = [
        {"name": "Herpex-Acyclovir 200mg", "id": 1},
        {"name": "Lovire", "id": 3},
        {"name": "Benkil 400", "id": 8}
    ]

    recent_events = [
        {"user": "adi eyal", "description": "Added purchase information.", "date": "2014-03-30"},
        {"user": "pjvr", "description": "Added purchase information.", "date": "2014-03-10"},
        {"user": "someone else", "description": "Added purchase information.", "date": "2014-02-15"},
        {"user": "adi eyal", "description": "Added purchase information.", "date": "2014-03-30"},
        {"user": "pjvr", "description": "Added purchase information.", "date": "2014-03-10"},
        {"user": "someone else", "description": "Added purchase information.", "date": "2014-02-15"}
    ]

    count_products = 50
    count_transactions = 450

    flash("it is now: " + str(datetime.datetime.now()), "success")
    flash("it is still: " + str(datetime.datetime.now()), "info")
    flash("it is even still: " + str(datetime.datetime.now()), "warning")

    return render_template(
        'index.html',
        active_nav_button="home",
        top_sources=top_sources,
        count_products=count_products,
        count_transactions=count_transactions,
        recent_products=recent_products,
        recent_events=recent_events
    )

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