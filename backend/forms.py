import wtforms
from wtforms import Form
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, DateField
from wtforms import validators
from backend import app, db, logger
import models
from flask.ext.admin.form import widgets, fields


incoterm_choices = []
incoterms = models.Incoterm.query.order_by(models.Incoterm.code).all()
for incoterm in incoterms:
    incoterm_choices.append((incoterm.incoterm_id, incoterm.code + " (" + incoterm.description + ")"))

country_choices = []
countries = models.Country.query.all()
for country in countries:
    country_choices.append((country.country_id, country.name))

method_choices = [
    ('tender', 'tender'),
    ('direct procurement', 'direct procurement'),
    (None, 'unknown')
]

medicine_choices = []
medicines = models.Medicine.query.order_by(models.Medicine.name).all()
for medicine in medicines:
    medicine_choices.append((medicine.medicine_id, medicine.name + " - " + str(medicine.dosage_form)))


product_choices = []
products = models.Product.query.all()
for product in products:
    product_choices.append((product.product_id, str(product)))


class ProcurementForm(Form):

    country = fields.Select2Field('Country', [validators.InputRequired()], choices=country_choices)
    product = fields.Select2Field('Product', [validators.InputRequired()], choices=product_choices)
    container = StringField('Container', [validators.Length(max=50)])
    pack_size = IntegerField('Pack size', [validators.InputRequired()])
    pack_price = FloatField('Pack price', [validators.InputRequired()])
    quantity = IntegerField('Quantity', [validators.InputRequired()])
    method = SelectField('Method', choices=method_choices)
    start_date = DateField('Start date', [validators.InputRequired()], widget=widgets.DatePickerWidget())
    end_date = DateField('End date', [validators.InputRequired()], widget=widgets.DatePickerWidget())
    incoterm = SelectField('Incoterm', [validators.InputRequired()], choices=incoterm_choices)

