from main import db, logger
import serializers
from sqlalchemy.orm import backref
import datetime
from openexchangerates import OpenExchangeRates

def avg(list):

    if len(list) == 0:
        return float(0)
    return sum(list) / float(len(list))


class MyModel(db.Model):

    def __init__(self, serializer_class=serializers.BaseSerializer):
        self.serializer = serializer_class()
        self.to_json = self.serializer.to_json
        super(MyModel, self).__init__()


class Source(MyModel):

    country_id = db.Column(db.Integer, primary_key=True)
    name = name = db.Column(db.String(250))
    date = db.Column(db.Date, default=datetime.datetime.now)
    url = db.Column(db.String(250))  # Provide a link to the source document for reference purposes. Ideally, load the document into the Infohub CKAN installation at data.medicinesinfohub.net and add the link to the source of the document as an additional

    def __unicode__(self):
        s = u'%s @ %s' % (self.name, self.date)
        return s


class Country(MyModel):

    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    code = db.Column(db.String(3))

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code.upper())


class Incoterm(MyModel):

    incoterm_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(3))
    description = db.Column(db.String(128))

    def __unicode__(self):
        return u'%s' % (self.name)


class DosageForm(MyModel):

    dosage_form_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))

    def as_dict(self, minimal=False):
        return self.name

    def __unicode__(self):
        return u'%s' % (self.name)


class Medicine(MyModel):

    medicine_id = db.Column(db.Integer, primary_key=True)
    
    dosage_form_id = db.Column(db.Integer, db.ForeignKey('dosage_form.dosage_form_id'), nullable=True)
    dosage_form = db.relationship('DosageForm')

    @property
    def name(self):
        out = None
        if self.ingredients.count() > 0:
            out = " + ".join([i.ingredient.name.capitalize() for i in self.ingredients])
        return out

    @property
    def average_price(self):
        sum = 0
        tot = 0
        procurements = Procurement.query.filter(medicine_id=self.medicine_id).all()
        for p in procurements:
            sum += p.price_usd * p.volume
            tot += p.container.quantity * p.volume
        if tot > 0:
            return sum/tot
        return None

    def __unicode__(self):
        return u'%s %s' % (self.name, self.dosage_form)


class Component(MyModel):

    component_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Ingredient(MyModel):

    ingredient_id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(16))

    component_id = db.Column(db.Integer, db.ForeignKey('component.component_id'), nullable=True)
    component = db.relationship('Component')
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref=backref("ingredients"))

    def __unicode__(self):
        return u'%s %s' % (self.component.name, self.strength)


class BenchmarkPrice(MyModel):

    __table_args__ = (db.UniqueConstraint('medicine', 'year', 'name'), {})

    benchmark_price_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # this should be restricted by a select field in the Admin interface
    price = db.Column(db.Float)  # The benchmark price for the medicine.
    year = db.Column(db.Integer, nullable=False)

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref="benchmarks")

    def __unicode__(self):
        return u'%s @ %.4f' % (self.medicine, self.price)


class Manufacturer(MyModel):

    manufacturer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    website = db.Column(db.String(250))  # e.g. http://www.example.com, ensure that the leading http:// is included")

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.country.code.upper() if self.country else "No Country")


class Site(MyModel):

    site_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    street_address = db.Column(db.String(250))

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.manufacturer.name)


class Supplier(MyModel):

    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    street_address = db.Column(db.String(500))
    website = db.Column(db.String(250))
    contact = db.Column(db.String(64))
    phone = db.Column(db.String(16))
    alt_phone = db.Column(db.String(16))
    fax = db.Column(db.String(16))
    email = db.Column(db.String(100))
    alt_email = db.Column(db.String(100))
    authorized = db.Column(db.Boolean, default=False)

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')

    def __unicode__(self):
        return u'%s' % (self.name)


class Product(MyModel):

    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64, blank=True))
    generic = db.Column(db.Boolean, default=True)

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref('products'))
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer')
    site_id = db.Column(db.Integer, db.ForeignKey('site.site_id'), nullable=True)
    site = db.relationship('Site')

    def __unicode__(self):
        if self.name:
            return u'%s - %s (%s)' % (self.name, self.manufacturer, str(self.medicine))
        return u'%s (%s)' % (self.manufacturer, str(self.medicine))


class Container(MyModel):

    container_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))  # This should be the actual type of containter that the medicine is distributed in eg. bottle, blister pack, tube etc.
    unit = db.Column(db.String(32))  # This represents the basic unit of measure for this container eg. ml (for a bottled suspension), g (for a tube of ointment) or tablet/capsule (for a bottle of tablets/capsules).
    quantity = db.Column(db.Float)  # The total container size eg. 100 (for a 100ml bottle), 50 (for a bottle of 50 tablets) or 3.5 (for a 3.5g tube of ointment).

    def __unicode__(self):
        return u'%.7g %s %s' % (self.quantity, self.unit, self.type)


class Registration(MyModel):

    registration_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(32))
    status = db.Column(db.Boolean, default=True)
    application_date = db.Column(db.Date, nullable=True)
    registration_date = db.Column(db.Date, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)

    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=True)
    product = db.relationship('Product')
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    site_id = db.Column(db.Integer, db.ForeignKey('site.site_id'), nullable=True)
    site = db.relationship('Site')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)
    supplier = db.relationship('Supplier')
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')

    def __unicode__(self):
        return u'%s - %s' % (self.number, self.product.name)


class Currency(MyModel):

    currency_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3))  # Enter the ISO 4217 currency code for the currency. This is a 3 letter code in all capitals eg. USD, ZAR etc.

    def __unicode__(self):
        return self.code


class Procurement(MyModel):

    procurement_id = db.Column(db.Integer, primary_key=True)
    pack_size = db.Column(db.Integer) # Enter the number of containers in the standard packaging eg. 100 bottles of paracetamol suspension per box.
    price = db.Column(db.Float) # Price per container. The procurement price should be entered in the currency that the purchase was made in and the currency must be indicated below. Note that a unit will be one unit of the container indicated above (eg. the price of one blister pack with 24 capsules in EUR).
    volume = db.Column(db.Integer) # The number of packages contracted at the specified unit price. Volume is calculated as # of packages * containers in pack', default=1)
    method = db.Column(db.String(100)) # Procurement Method. Open or restricted ICB, domestic tender, shopping, sole source.
    start_date = db.Column(db.Date, nullable=True) # This is the first day that the procurement price is valid for (may be left blank).
    end_date = db.Column(db.Date, nullable=True) # This is the last day that the procurement price is valid for (may be left blank).

    currency_id = db.Column(db.Integer, db.ForeignKey('currency.currency_id'), nullable=True)
    currency = db.relationship('Currency')  # This is the currency of the procurement price. This field is required to convert units to USD for comparison.
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=True)
    product = db.relationship('Product')
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)
    supplier = db.relationship('Supplier')
    container_id = db.Column(db.Integer, db.ForeignKey('container.container_id'), nullable=True)
    container = db.relationship('Container')  # Indicate the container that the medication is distributed in eg. 100 ml bottle for a paracetamol suspension.
    incoterm_id = db.Column(db.Integer, db.ForeignKey('incoterm.incoterm_id'), nullable=True)
    incoterm = db.relationship('Incoterm')  # The international trade term applicable to the contracted price. Ideally this should be standardised as FOB or EXW to allow comparability.
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')

    @property
    def price_usd(self):
        c = currency.models.Currency.objects.get(code=self.currency.code)
        if c.code == 'USD':
            return self.price
        e = currency.models.ExchangeRate.objects.get(currency=c, date=self.start_date)
        return self.price/e.rate

    @property
    def price_per_unit(self):
        if self.container.quantity:
            return self.price_usd / self.container.quantity
        return None

    def __unicode__(self):
        if self.volume:
            return u'%d x %s' % (self.volume, self.product.__unicode__())
        return u'unknown quantity x %s' % (self.product.__unicode__())


class Context(MyModel):

    context_id = db.Column(db.Integer, primary_key=True)
    population = db.Column(db.Integer)
    gni_per_capita = db.Column(db.Float)
    nmra_name = db.Column(db.String(32))
    nmra_website = db.Column(db.String(250))
    pspa_name = db.Column(db.String(32))
    pspa_website = db.Column(db.String(250))
    nmpa_name = db.Column(db.String(32))
    nmpa_website = db.Column(db.String(250))
    nmpa_status = db.Column(db.String(32)) # e.g. MOH department, public company, NGO.
    budget = db.Column(db.Float) # Annual public sector pharmaceutical procurement budget (USD), including all relevant on-budget budget lines (e.g. including vertical programmes, NMPA, districts, hospitals as adequate).
    tender_time = db.Column(db.Integer) # Number of months from selection and quantification up to contract award; for open or restricted ICB only.
    tender_currencies = db.Column(db.String(32))
    payment_terms = db.Column(db.String(32))  # Payment terms/modalities, e.g. Letter of Credit, other forms of pre-payment against performance guarantee, on account (XX days).
    local_preference = db.Column(db.String(64))  # Figure and requirements applicable to local preference.
    import_duty = db.Column(db.Float) # Import duties and taxes, % figure as applicable.
    freight = db.Column(db.Float) # Average cost for freight & insurance, % figure.

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')

    def __unicode__(self):
        return u'%d x %s' % (self.volume, self.product.name)
