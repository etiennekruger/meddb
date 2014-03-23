from flask import render_template
from frontend import app
import requests

@app.route('/')
def root():

    return render_template('index.html', active_nav_button="home")


@app.route('/medicine/')
def medicine_index():

    response = requests.get('http://127.0.0.1:8000/json/medicine/')
    medicine_list = response.json()
    return render_template('medicine_index.html', medicine_list=medicine_list, active_nav_button="medicines")


@app.route('/medicine/<medicine_id>/')
def medicine(medicine_id):

    response = requests.get('http://127.0.0.1:8000/json/medicine/' + str(medicine_id) + "/")
    medicine = response.json()
    return render_template('medicine.html', medicine=medicine, active_nav_button="medicines")


@app.route('/supplier/')
def supplier_index():

    response = requests.get('http://127.0.0.1:8000/json/supplier/')
    supplier_list = response.json()
    return render_template('supplier_index.html', supplier_list=supplier_list, active_nav_button="suppliers")


@app.route('/supplier/<supplier_id>/')
def supplier(supplier_id):

    response = requests.get('http://127.0.0.1:8000/json/supplier/' + str(supplier_id) + "/")
    supplier = response.json()
    return render_template('supplier.html', supplier=supplier, active_nav_button="suppliers")