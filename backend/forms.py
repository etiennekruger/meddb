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

container_choices = []
containers = models.AvailableContainers.query.all()
for container in containers:
    container_choices.append((str(container), str(container)))

procurement_method_choices = []
procurement_methods = models.AvailableProcurementMethods.query.all()
for procurement_method in procurement_methods:
    procurement_method_choices.append((str(procurement_method), str(procurement_method)))


def get_product_choices():
    product_choices = []
    products = models.Product.query.all()
    for product in products:
        product_choices.append((product.product_id, str(product)))
    return product_choices


def get_supplier_choices():
    supplier_choices = []
    suppliers = models.Supplier.query.all()
    for supplier in suppliers:
        supplier_choices.append((supplier.supplier_id, str(supplier)))
    return supplier_choices


class ProcurementForm(Form):

    country = fields.Select2Field('Country', [validators.InputRequired()], coerce=int, choices=country_choices, description="The country that made the procurement.")
    product = fields.Select2Field('Product', [validators.InputRequired()], coerce=int, description="Product = Medicine + Manufacturer + Site")
    supplier = fields.Select2Field('Supplier', [validators.InputRequired()], coerce=int, description="The Supplier may be the same as the Manufacturer")
    container = SelectField('Container', choices=container_choices, description="How is the medicine packaged?")
    pack_size = IntegerField('Pack size', [validators.InputRequired()], description="How many <span class='uom-placeholder'>unit</span>s are there in a pack?")
    pack_price = FloatField('Pack price', [validators.InputRequired()], description='What is the price of one <span class="container-placeholder">pack</span>?')
    currency = fields.Select2Field('Currency', [validators.InputRequired()], coerce=int, choices=currency_choices, description="Select the currency of the transaction.")
    pack_price_usd = FloatField('Pack price in USD', [validators.InputRequired()])
    unit_price_usd = FloatField('Unit price in USD', [validators.InputRequired()], description="This is the price we use for making comparisons ($ per <span class='uom-placeholder'>unit</span>).")
    quantity = IntegerField('Quantity', [validators.InputRequired()], description="How many packs were bought/contracted at this price?")
    method = SelectField('Method', choices=procurement_method_choices)
    start_date = DateField('Start date', [validators.InputRequired()], format="%Y-%m-%d", widget=widgets.DatePickerWidget(), description="From when was this price valid?")
    end_date = DateField('End date', [validators.InputRequired()], widget=widgets.DatePickerWidget(), description="Until when does the price stay valid?")
    incoterm = SelectField('Incoterm', [validators.InputRequired()], coerce=int, choices=incoterm_choices)

