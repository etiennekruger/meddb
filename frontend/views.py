from flask import render_template
from frontend import app

@app.route('/')
def root():

    return render_template('index.html')