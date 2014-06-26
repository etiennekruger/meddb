from backend import app, db, logger
import serializers
from sqlalchemy.orm import backref
import datetime
from openexchangerates import OpenExchangeRates

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))
    activated = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')

    def is_active(self):
        return self.activated

    def is_authenticated(self):
        return True

    def get_id(self):
        return unicode(self.user_id)

    def __repr__(self):
        return self.email

    def to_dict(self, include_related=False):
        return {'user_id': self.user_id, 'email': self.email}


class Source(db.Model):

    __tablename__ = "source"
    source_id = db.Column(db.Integer, primary_key=True)
    name = name = db.Column(db.String(250))
    date = db.Column(db.Date, nullable=True)
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
    code_short = db.Column(db.String(2))

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
    name = db.Column(db.String(100), unique=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Medicine(db.Model):

    __tablename__ = "medicine"
    medicine_id = db.Column(db.Integer, primary_key=True)
    alternative_names = db.Column(db.String(100), default=None)
    dosage_form_id = db.Column(db.Integer, db.ForeignKey('dosage_form.dosage_form_id'), nullable=True)
    dosage_form = db.relationship('DosageForm')

    @property
    def name(self):
        out = "Unnamed Medicine"
        if len(self.components) > 0:
            component_names = []
            for component in self.components:
                tmp = component.ingredient.name.capitalize()
                if component.strength:
                    tmp += " (" + str(component.strength) + ")"
                component_names.append(tmp)
            out = ", ".join(component_names)
        return out

    @property
    def procurements(self):
        out = []
        products = Product.query.filter(Product.medicine_id == self.medicine_id).all()
        if products:
            for product in products:
                out += product.procurements
        return out

    def __unicode__(self):
        return u'%s %s' % (self.name, self.dosage_form)

    def to_dict(self, include_related=False):
        return serializers.medicine_to_dict(self, include_related)


class Ingredient(db.Model):

    __tablename__ = "ingredient"
    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __unicode__(self):
        return u'%s' % self.name

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
        return serializers.component_to_dict(self, include_related)


class BenchmarkPrice(db.Model):

    __tablename__ = "benchmark_price"
    __table_args__ = (db.UniqueConstraint('medicine_id', 'year', 'name'), {})

    benchmark_price_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # this should be restricted by a select field in the Admin interface
    price = db.Column(db.Float)  # The benchmark price for the medicine.
    unit_of_measure = db.Column(db.String(50))
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
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    added_by = db.relationship('User', foreign_keys=added_by_id, backref='manufacturers_added')

    def get_name(self):
        tmp = "Unnamed Manufacturer"
        if self.name:
            tmp = self.name
        return tmp

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
    manufacturer = db.relationship('Manufacturer', backref='sites')

    def __unicode__(self):
        return unicode(self.name)

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
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    added_by = db.relationship('User', foreign_keys=added_by_id, backref='suppliers_added')

    @property
    def products(self):
        out = []
        if self.procurements:
            for procurement in self.procurements:
                if not (procurement.product in out):
                    out.append(procurement.product)
        return out

    def __unicode__(self):
        return u'%s' % (self.name)

    def to_dict(self, include_related=False):
        return serializers.supplier_to_dict(self, include_related)


class Product(db.Model):

    __tablename__ = "product"
    product_id = db.Column(db.Integer, primary_key=True)
    average_price = db.Column(db.Float, nullable=True)
    name = db.Column(db.String(64), nullable=True)
    is_generic = db.Column(db.Boolean, default=True)
    shelf_life = db.Column(db.String, nullable=True)

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref='products')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer')
    site_id = db.Column(db.Integer, db.ForeignKey('site.site_id'), nullable=True)
    site = db.relationship('Site')
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    added_by = db.relationship('User', foreign_keys=added_by_id, backref='products_added')

    def calculate_average_price(self):
        sum = 0
        tot = 0
        for p in self.procurements:
            if p.pack_price_usd and p.quantity:
                sum += p.pack_price_usd * p.quantity
                num_units = p.quantity
                if p.pack_size:
                    num_units *= p.pack_size
                tot += num_units
        if tot > 0:
            self.average_price = sum/tot
        return

    def get_name(self):
        if self.name:
            tmp = self.name
        else:
            tmp = self.medicine.name
        return tmp

    @property
    def alternative_products(self):
        out = []
        products = Product.query.filter(Product.medicine_id == self.medicine_id).all()
        if len(products) > 1:
            for product in products:
                if not product == self:
                    out.append(product)
        return out

    def __unicode__(self):
        if self.name:
            return u'%s (%s), %s' % (self.name, self.medicine, self.manufacturer)
        return u'%s, %s' % (self.medicine, self.manufacturer)

    def to_dict(self, include_related=False):
        return serializers.product_to_dict(self, include_related)


class AvailableContainers(db.Model):

    __tablename__ = "available_containers"
    container_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50))

    def __unicode__(self):
        return u'%s' % self.value


class AvailableUnits(db.Model):

    __tablename__ = "available_units"
    unit_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(32))

    def __unicode__(self):
        return u'%s' % self.value


class Registration(db.Model):

    __tablename__ = "registration"
    registration_id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(32))
    application_year = db.Column(db.Integer, nullable=True)
    registration_date = db.Column(db.Date, nullable=True)
    expired = db.Column(db.Boolean, default=False)

    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=True)
    product = db.relationship('Product', backref='registrations')
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.number, self.product.name, self.country.code)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Procurement(db.Model):

    __tablename__ = "procurement"
    procurement_id = db.Column(db.Integer, primary_key=True)
    container = db.Column(db.String(50))
    pack_size = db.Column(db.Integer) # the number of basic units per pack, for which the price is quoted.
    unit_of_measure = db.Column(db.String(50))
    pack_price = db.Column(db.Float) # Price per container. The procurement price should be entered in the currency that the procurement was made in and the currency must be indicated below. Note that a unit will be one unit of the container indicated above (eg. the price of one blister pack with 24 capsules in EUR).
    pack_price_usd = db.Column(db.Float, nullable=False) # per container
    unit_price_usd = db.Column(db.Float) # this is always in USD
    quantity = db.Column(db.Integer, nullable=False) # The number of packages contracted at the specified unit price.
    method = db.Column(db.String(100)) # Procurement Method. Open or restricted ICB, domestic tender, shopping, sole source.
    start_date = db.Column(db.Date, nullable=False) # This is the first day that the procurement price is valid for (may be left blank).
    end_date = db.Column(db.Date, nullable=True) # This is the last day that the procurement price is valid for (may be left blank).
    incoterm = db.Column(db.String(3), nullable=True)  # The international trade term applicable to the contracted price. Ideally this should be standardised as FOB or EXW to allow comparability.
    added_on = db.Column(db.Date, default=datetime.datetime.today())
    approved_on = db.Column(db.Date, nullable=True)

    currency_id = db.Column(db.Integer, db.ForeignKey('currency.currency_id'), nullable=False)
    currency = db.relationship('Currency', backref='procurements')
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    product = db.relationship('Product', backref='procurements')
    incoterm_id = db.Column(db.Integer, db.ForeignKey('incoterm.incoterm_id'), nullable=True)
    incoterm = db.relationship('Incoterm')
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)
    supplier = db.relationship('Supplier', backref='procurements')
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    added_by = db.relationship('User', foreign_keys=added_by_id, backref='procurements_added')
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    approved_by = db.relationship('User', foreign_keys=approved_by_id, backref='procurements_approved')

    def __unicode__(self):
        if self.volume:
            return u'%d x %s' % (self.volume, self.product.__unicode__())
        return u'unknown quantity x %s' % (self.product.__unicode__())

    def to_dict(self, include_related=False):
        return serializers.procurement_to_dict(self, include_related)
