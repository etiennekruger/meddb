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
    country_choices.append((country.country_id, unicode(country)))

currency_choices = []
currencies = models.Currency.query.all()
for currency in currencies:
    currency_choices.append((currency.currency_id, unicode(currency)))

medicine_choices = []
medicines = models.Medicine.query.order_by(models.Medicine.name).all()
for medicine in medicines:
    medicine_choices.append((medicine.medicine_id, medicine.name + " - " + str(medicine.dosage_form)))

product_choices = []
products = models.Product.query.all()
for product in products:
    product_choices.append((product.product_id, str(product)))

supplier_choices = []
suppliers = models.Supplier.query.all()
for supplier in suppliers:
    supplier_choices.append((supplier.supplier_id, str(supplier)))

container_choices = []
containers = models.AvailableContainers.query.all()
for container in containers:
    container_choices.append((str(container), str(container)))

procurement_method_choices = []
procurement_methods = models.AvailableProcurementMethods.query.all()
for procurement_method in procurement_methods:
    procurement_method_choices.append((str(procurement_method), str(procurement_method)))


class ProcurementForm(Form):

    country = fields.Select2Field('Country', [validators.InputRequired()], coerce=int, choices=country_choices)
    product = fields.Select2Field('Product', [validators.InputRequired()], coerce=int, choices=product_choices)
    supplier = fields.Select2Field('Supplier', [validators.InputRequired()], coerce=int, choices=supplier_choices)
    container = SelectField('Container', choices=container_choices)
    pack_size = IntegerField('Pack size', [validators.InputRequired()])
    pack_price = FloatField('Pack price', [validators.InputRequired()])
    currency = fields.Select2Field('Currency', [validators.InputRequired()], coerce=int, choices=currency_choices)
    pack_price_usd = FloatField('Pack price in USD', [validators.InputRequired()])
    unit_price_usd = FloatField('Unit price in USD', [validators.InputRequired()])
    quantity = IntegerField('Quantity', [validators.InputRequired()])
    method = SelectField('Method', choices=procurement_method_choices)
    start_date = DateField('Start date', [validators.InputRequired()], format="%Y-%m-%d", widget=widgets.DatePickerWidget())
    end_date = DateField('End date', [validators.InputRequired()], widget=widgets.DatePickerWidget())
    incoterm = SelectField('Incoterm', [validators.InputRequired()], coerce=int, choices=incoterm_choices)

