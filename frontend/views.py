from flask import render_template, flash, redirect, request
from frontend import app, logger
import requests
import operator
import dateutil.parser
import datetime

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


@app.route('/')
def landing():

    recent_products = [
        {"name": "Herpex-Acyclovir 200mg", "id": 1},
        {"name": "Lovire", "id": 3},
        {"name": "Benkil 400", "id": 8}
    ]

    tmp_response = requests.get(API_HOST + 'recent_updates/')
    recent_updates = tmp_response.json()['results']

    tmp_response = requests.get(API_HOST + 'overview/')
    overview = tmp_response.json()

    return render_template(
        'index.html',
        API_HOST=API_HOST,
        active_nav_button="home",
        overview=overview,
        recent_products=recent_products,
        recent_updates=recent_updates
    )


@app.route('/medicine/<medicine_id>/')
def medicine(medicine_id):

    response = requests.get(API_HOST + 'medicine/' + str(medicine_id) + "/")
    medicine = response.json()

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

@app.route('/procurement/<procurement_id>/')
def procurement(procurement_id):

    response = requests.get(API_HOST + 'procurement/' + str(procurement_id) + "/")
    procurement = response.json()
    return render_template(
        'procurement.html',
        API_HOST=API_HOST,
        procurement=procurement,
        active_nav_button="procurement"
    )

@app.route('/admin/')
def admin_redirect():
    return redirect(API_HOST + "admin/")


@app.route('/meddb/')
def legacy_redirect():
    return redirect("/", 301)