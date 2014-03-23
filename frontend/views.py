from flask import render_template
from frontend import app
import requests

@app.route('/')
def root():

    return render_template('index.html', active_nav_button="home")


@app.route('/medicines')
def medicines():

    response = requests.get('http://127.0.0.1:8000/json/medicine/')
    medicine_list = response.json()
    return render_template('medicines.html', medicine_list=medicine_list, active_nav_button="medicines")


@app.route('/suppliers')
def suppliers():

    return render_template('suppliers.html', active_nav_button="suppliers")