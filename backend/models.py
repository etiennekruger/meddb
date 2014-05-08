from backend import app, db, logger
import serializers
from sqlalchemy.orm import backref
import datetime
import json
from openexchangerates import OpenExchangeRates
import serializers


class Source(db.Model):

    __tablename__ = "source"
    source_id = db.Column(db.Integer, primary_key=True)
    name = name = db.Column(db.String(250))
    date = db.Column(db.Date, default=datetime.datetime.now)
    url = db.Column(db.String(250), nullable=True)  # Provide a link to the source document for reference purposes. Ideally, load the document into the Infohub CKAN installation at data.medicinesinfohub.net and add the link to the source of the document as an additional

    def __unicode__(self):
        s = u'%s @ %s' % (self.name, self.date)
        return s

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Country(db.Model):

    __tablename__ = "country"
    country_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(3))

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code.upper())

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Currency(db.Model):

    __tablename__ = "currency"
    currency_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(3))

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code.upper())

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Incoterm(db.Model):

    __tablename__ = "incoterm"
    incoterm_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100))
    code = db.Column(db.String(3))

    def __unicode__(self):
        return u'(%s) %s' % (self.code.upper(), self.description)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class DosageForm(db.Model):

    __tablename__ = "dosage_form"
    dosage_form_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __unicode__(self):
        return u'%s' % (self.name)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Medicine(db.Model):

    __tablename__ = "medicine"
    medicine_id = db.Column(db.Integer, primary_key=True)
    average_price = db.Column(db.Float, nullable=True)
    dosage_form_id = db.Column(db.Integer, db.ForeignKey('dosage_form.dosage_form_id'), nullable=True)
    dosage_form = db.relationship('DosageForm')

    @property
    def name(self):
        out = None
        if len(self.components) > 0:
            out = " + ".join([component.ingredient.name.capitalize() for component in self.components])
        return out

    def calculate_average_price(self):
        sum = 0
        tot = 0
        products = Product.query.filter(Product.medicine_id == self.medicine_id).all()
        for product in products:
            procurements = Procurement.query.filter(Product.product_id == product.product_id).all()
            for p in procurements:
                if p.price_usd and p.volume and p.container.quantity:
                    sum += p.price_usd * p.volume
                    tot += p.container.quantity * p.volume
        if tot > 0:
            self.average_price = sum/tot
        return

    def __unicode__(self):
        return u'%s %s' % (self.name, self.dosage_form)

    def to_dict(self, include_related=False):
        return serializers.medicine_to_dict(self, include_related)


class Ingredient(db.Model):

    __tablename__ = "ingredient"
    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Component(db.Model):

    __tablename__ = "component"
    component_id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(16))

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'), nullable=True)
    ingredient = db.relationship('Ingredient')
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref=backref("components"))

    def __unicode__(self):
        return u'%s %s' % (self.ingredient.name, self.strength)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class BenchmarkPrice(db.Model):

    __tablename__ = "benchmark_price"
    __table_args__ = (db.UniqueConstraint('medicine_id', 'year', 'name'), {})

    benchmark_price_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # this should be restricted by a select field in the Admin interface
    price = db.Column(db.Float)  # The benchmark price for the medicine.
    year = db.Column(db.Integer, nullable=False)

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref="benchmarks")

    def __unicode__(self):
        return u'%s @ %.4f' % (self.medicine, self.price)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Manufacturer(db.Model):

    __tablename__ = "manufacturer"
    manufacturer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    website = db.Column(db.String(250))  # e.g. http://www.example.com, ensure that the leading http:// is included")

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.country.code.upper() if self.country else "No Country")

    def to_dict(self, include_related=False):
        return serializers.manufacturer_to_dict(self, include_related)


class Site(db.Model):

    __tablename__ = "site"
    site_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    street_address = db.Column(db.String(250))

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.manufacturer.name)

    def to_dict(self, include_related=False):
        return serializers.site_to_dict(self, include_related)


class Supplier(db.Model):

    __tablename__ = "supplier"
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

    def to_dict(self, include_related=False):
        return serializers.supplier_to_dict(self, include_related)


class Product(db.Model):

    __tablename__ = "product"
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    is_generic = db.Column(db.Boolean, default=True)

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref='products')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer')
    site_id = db.Column(db.Integer, db.ForeignKey('site.site_id'), nullable=True)
    site = db.relationship('Site')

    def __unicode__(self):
        if self.name:
            return u'%s - %s (%s)' % (self.name, self.manufacturer, str(self.medicine))
        return u'%s (%s)' % (self.manufacturer, str(self.medicine))

    def to_dict(self, include_related=False):
        return serializers.product_to_dict(self, include_related)


class Container(db.Model):

    __tablename__ = "container"
    container_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))  # This should be the actual type of containter that the medicine is distributed in eg. bottle, blister pack, tube etc.
    unit = db.Column(db.String(32))  # This represents the basic unit of measure for this container eg. ml (for a bottled suspension), g (for a tube of ointment) or tablet/capsule (for a bottle of tablets/capsules).
    quantity = db.Column(db.Float)  # The total container size eg. 100 (for a 100ml bottle), 50 (for a bottle of 50 tablets) or 3.5 (for a 3.5g tube of ointment).

    def __unicode__(self):
        return u'%.7g %s %s' % (self.quantity, self.unit, self.type)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Registration(db.Model):

    __tablename__ = "registration"
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

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Procurement(db.Model):

    __tablename__ = "procurement"
    procurement_id = db.Column(db.Integer, primary_key=True)
    pack_size = db.Column(db.Integer) # Enter the number of containers in the standard packaging eg. 100 bottles of paracetamol suspension per box.
    price = db.Column(db.Float) # Price per container. The procurement price should be entered in the currency that the purchase was made in and the currency must be indicated below. Note that a unit will be one unit of the container indicated above (eg. the price of one blister pack with 24 capsules in EUR).
    price_usd = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Integer) # The number of packages contracted at the specified unit price. Volume is calculated as # of packages * containers in pack', default=1)
    method = db.Column(db.String(100)) # Procurement Method. Open or restricted ICB, domestic tender, shopping, sole source.
    start_date = db.Column(db.Date, nullable=True) # This is the first day that the procurement price is valid for (may be left blank).
    end_date = db.Column(db.Date, nullable=True) # This is the last day that the procurement price is valid for (may be left blank).
    incoterm = db.Column(db.String(3), nullable=True)  # The international trade term applicable to the contracted price. Ideally this should be standardised as FOB or EXW to allow comparability.
    currency = db.Column(db.String(3), nullable=True)  # This is the currency of the procurement price. This field is required to convert units to USD for comparison.

    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=True)
    product = db.relationship('Product', backref='procurements')
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)
    supplier = db.relationship('Supplier')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer')
    container_id = db.Column(db.Integer, db.ForeignKey('container.container_id'), nullable=True)
    container = db.relationship('Container')  # Indicate the container that the medication is distributed in eg. 100 ml bottle for a paracetamol suspension.
    # source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    # source = db.relationship('Source')

    def calculate_price_usd(self):
        if self.currency_code == 'USD':
            self.price_usd = self.price
            return
        e = OpenExchangeRates()
        try:
            rate = e.convert_to_usd(currency=self.currency_code, date=self.start_date)
            self.price_usd = self.price/rate
        except IOError as e:
            logger.error("Cannot connect to OpenExchangeRates API: " + str(e))
            raise
        except Exception as e:
            logger.error("Error converting between currencies: " + str(e))
            raise
        return

    @property
    def price_per_unit(self):
        if self.container.quantity and self.price_usd:
            return self.price_usd / self.container.quantity
        return None

    def __unicode__(self):
        if self.volume:
            return u'%d x %s' % (self.volume, self.product.__unicode__())
        return u'unknown quantity x %s' % (self.product.__unicode__())

    def to_dict(self, include_related=False):
        return serializers.procurement_to_dict(self, include_related)
