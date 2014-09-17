import wtforms
from wtforms import Form
from wtforms import StringField, PasswordField, SelectField, IntegerField, FloatField, DateField
from wtforms import validators
from backend import app, db, logger
import models
import widgets
import fields


incoterm_choices = []
incoterms = models.Incoterm.query.order_by(models.Incoterm.code).all()
for incoterm in incoterms:
    incoterm_choices.append((incoterm.incoterm_id, incoterm.code + " (" + incoterm.description + ")"))

available_countries = {
    "AGO":  "Angola",
    "BWA":  "Botswana",
    "COD":  "DRC",
    "LSO":  "Lesotho",
    "MDG":  "Madagascar",
    "MWI":  "Malawi",
    "MUS":  "Mauritius",
    "MOZ":  "Mozambique",
    "NAM":  "Namibia",
    "SYC":  "Seychelles",
    "ZAF":  "South Africa",
    "SWZ":  "Swaziland",
    "TZA":  "Tanzania",
    "ZMB":  "Zambia",
    "ZWE":  "Zimbabwe",
    }

country_choices = [(key, value) for key, value in available_countries.iteritems()]

method_choices = [
    ('tender', 'tender'),
    ('direct procurement', 'direct procurement'),
    (None, 'unknown')
]

medicine_choices = []
medicines = models.Medicine.query.order_by(models.Medicine.name).all()
for medicine in medicines:
    medicine_choices.append((medicine.medicine_id, medicine.name + " - " + str(medicine.dosage_form)))


class ProcurementForm(Form):

    country = fields.Select2Field('Country', [validators.InputRequired()], choices=country_choices)
    medicine = SelectField('Medicine', [validators.InputRequired()], choices=medicine_choices)
    container = StringField('Container', [validators.Length(max=50)])
    pack_size = IntegerField('Pack size', [validators.InputRequired()])
    pack_price = FloatField('Pack price', [validators.InputRequired()])
    quantity = IntegerField('Quantity', [validators.InputRequired()])
    method = SelectField('Method', choices=method_choices)
    start_date = DateField('Start date', [validators.InputRequired()], widget=widgets.DatePickerWidget())
    end_date = DateField('End date', [validators.InputRequired()], widget=widgets.DatePickerWidget())
    incoterm = SelectField('Incoterm', [validators.InputRequired()], choices=incoterm_choices)

