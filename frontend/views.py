from flask import render_template
from frontend import app
import requests
import dateutil.parser

api_host = app.config['API_HOST']

@app.template_filter('format_date')
def jinja2_filter_format_date(date_str):
    date = dateutil.parser.parse(date_str)
    native = date.replace(tzinfo=None)
    format='%b %Y'
    return native.strftime(format)

@app.route('/')
def root():

    return render_template('index.html', active_nav_button="home")


@app.route('/medicine/')
def medicine_index():

    response = requests.get(api_host + 'medicine/')
    medicine_list = response.json()
    return render_template('medicine_index.html', medicine_list=medicine_list, active_nav_button="medicines")


@app.route('/medicine/<medicine_id>/')
def medicine(medicine_id):

    response = requests.get(api_host + 'medicine/' + str(medicine_id) + "/")
    medicine = response.json()

    graph_data = []
    labels = []
    max_price = 0
    if medicine.get('procurements'):
        for i in range(len(medicine['procurements'])):
            procurement = medicine['procurements'][i]
            graph_data.append([procurement['price_per_unit'], i])
            packing = str(procurement['container']['quantity']) + " " + str(procurement['container']['unit']) + " " + procurement['container']['type']
            labels.append([i, str(procurement['country']['name'] + " - " + packing)])
            if procurement['price_per_unit'] > max_price:
                max_price = procurement['price_per_unit']

    return render_template('medicine.html',
                           medicine=medicine,
                           active_nav_button="medicines",
                           graph_data=graph_data,
                           labels=labels,
                           max_price=max_price)


@app.route('/product/<product_id>/')
def product(product_id):

    response = requests.get(api_host + 'product/' + str(product_id) + "/")
    product = response.json()
    return render_template('product.html', product=product, active_nav_button="medicines")


@app.route('/supplier/')
def supplier_index():

    response = requests.get(api_host + 'supplier/')
    supplier_list = response.json()
    return render_template('supplier_index.html', supplier_list=supplier_list, active_nav_button="suppliers")


@app.route('/supplier/<supplier_id>/')
def supplier(supplier_id):

    response = requests.get(api_host + 'supplier/' + str(supplier_id) + "/")
    supplier = response.json()
    return render_template('supplier.html', supplier=supplier, active_nav_button="suppliers")


@app.route('/procurement/<procurement_id>/')
def procurement(procurement_id):

    response = requests.get(api_host + 'procurement/' + str(procurement_id) + "/")
    procurement = response.json()
    return render_template('procurement.html', procurement=procurement)