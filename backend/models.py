from backend import app, db, logger
import serializers
from sqlalchemy.orm import backref
from sqlalchemy import UniqueConstraint
import datetime
from passlib.apps import custom_app_context as pwd_context
import string
import random

MAX_AGE = app.config["MAX_AGE"]


class ApiKey(db.Model):

    __tablename__ = "api_key"

    api_key_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True, nullable=False)
    user = db.relationship('User')

    def generate_key(self):
        self.key=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))
        return

    def __unicode__(self):
        s = u'%s' % self.key
        return s

    def to_dict(self, include_related=False):
        return {'user_id': self.user_id, 'key': self.key}



class User(db.Model):

    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    activated = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def is_active(self):
        return self.activated

    def __unicode__(self):
        s = u'%s' % self.email
        return s

    def to_dict(self, include_related=False):
        return serializers.user_to_dict(self)


class Source(db.Model):

    __tablename__ = "source"
    __table_args__ = (UniqueConstraint('name', 'date', 'url', name='source_name_date_url'), {})

    source_id = db.Column(db.Integer, primary_key=True)
    name = name = db.Column(db.String(250), nullable=False)
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
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True)
    code_short = db.Column(db.String(2), unique=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code.upper())

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Currency(db.Model):

    __tablename__ = "currency"

    currency_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code.upper())

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Incoterm(db.Model):

    __tablename__ = "incoterm"

    incoterm_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(3), unique=True)

    def __unicode__(self):
        return u'(%s) %s' % (self.code.upper(), self.description)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class DosageForm(db.Model):

    __tablename__ = "dosage_form"

    dosage_form_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __unicode__(self):
        return u'%s' % (self.name)

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Medicine(db.Model):

    __tablename__ = "medicine"
    __table_args__ = (UniqueConstraint('name', 'dosage_form_id', name='medicine_name_dosage_form'), {})

    medicine_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    unit_of_measure_id = db.Column(db.Integer, db.ForeignKey('unit_of_measure.unit_of_measure_id'), nullable=False)
    unit_of_measure = db.relationship('UnitOfMeasure', lazy='joined')
    dosage_form_id = db.Column(db.Integer, db.ForeignKey('dosage_form.dosage_form_id'), nullable=False)
    dosage_form = db.relationship('DosageForm', lazy='joined', backref=backref("medicines", lazy='joined'))

    @property
    def procurements(self):
        out = []
        cutoff = datetime.date.today() - datetime.timedelta(days=MAX_AGE)
        products = Product.query.filter(Product.medicine_id == self.medicine_id).all()
        if products:
            for product in products:
                for procurement in product.procurements:
                    if procurement.approved:
                        if (procurement.start_date is None or procurement.start_date > cutoff) or (procurement.end_date is None or procurement.end_date > cutoff):
                            out.append(procurement)
        return out

    def __unicode__(self):
        return u'%s %s' % (self.name, self.dosage_form)

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self, include_related=False):
        return serializers.medicine_to_dict(self, include_related)


class BenchmarkPrice(db.Model):

    __tablename__ = "benchmark_price"
    __table_args__ = (db.UniqueConstraint('medicine_id', 'year', 'name', name='benchmark_price_medicine_year_name'), {})

    benchmark_price_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # this should be restricted by a select field in the Admin interface
    price = db.Column(db.Float, nullable=False)  # The benchmark price for the medicine.
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
    __table_args__ = (db.UniqueConstraint('name', 'country_id', name='manufacturer_name_country'), {})

    manufacturer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country', lazy='joined')
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    added_by = db.relationship('User', foreign_keys=added_by_id, backref='manufacturers_added')

    def get_name(self):
        tmp = "Unnamed Manufacturer"
        if self.name:
            tmp = self.name
        return tmp

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.country.code.upper() if self.country else "No Country")

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self, include_related=False):
        return serializers.manufacturer_to_dict(self, include_related)


class Site(db.Model):

    __tablename__ = "site"

    site_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    street_address = db.Column(db.String(250), nullable=True)

    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country', lazy='joined')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=False)
    manufacturer = db.relationship('Manufacturer', backref='sites')

    def __unicode__(self):
        return unicode(self.name)

    def to_dict(self, include_related=False):
        return serializers.site_to_dict(self, include_related)


class Supplier(db.Model):

    __tablename__ = "supplier"

    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
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

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self, include_related=False):
        return serializers.supplier_to_dict(self, include_related)


class Product(db.Model):

    __tablename__ = "product"
    __table_args__ = (db.UniqueConstraint('description', 'medicine_id', 'manufacturer_id', 'site_id', name='product_name_medicine_manufacturer_site'), {})

    product_id = db.Column(db.Integer, primary_key=True)
    average_price = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(64), nullable=True)
    is_generic = db.Column(db.Boolean, default=True)
    shelf_life = db.Column(db.String, nullable=True)

    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.medicine_id'), nullable=True)
    medicine = db.relationship('Medicine', backref='products', lazy='joined')
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.manufacturer_id'), nullable=True)
    manufacturer = db.relationship('Manufacturer', lazy='joined')
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
        try:
            out = u'%s' % self.medicine
            if self.description:
                out += u' (%s)' % self.description
            if self.manufacturer:
                out += u', %s' % self.manufacturer
            else:
                out += u', unknown manufacturer'
        except UnicodeEncodeError:
            out = "unnamed product"
            pass
        return out

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self, include_related=False):
        return serializers.product_to_dict(self, include_related)


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
    country = db.relationship('Country', lazy='joined')
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')

    def __unicode__(self):
        return u'%s - %s (%s)' % (self.number, self.product.medicine, self.country.code)

    def to_dict(self, include_related=False):
        return serializers.model_to_dict(self)


class Procurement(db.Model):

    __tablename__ = "procurement"

    procurement_id = db.Column(db.Integer, primary_key=True)
    container = db.Column(db.String(50))
    pack_size = db.Column(db.Integer) # the number of basic units per pack, for which the price is quoted.
    pack_price = db.Column(db.Float) # Price per container. The procurement price should be entered in the currency that the procurement was made in and the currency must be indicated below. Note that a unit will be one unit of the container indicated above (eg. the price of one blister pack with 24 capsules in EUR).
    pack_price_usd = db.Column(db.Float, nullable=False) # per container
    unit_price_usd = db.Column(db.Float) # this is always in USD
    quantity = db.Column(db.Integer, nullable=False) # The number of packages contracted at the specified unit price.
    method = db.Column(db.String(100)) # Procurement Method. Open or restricted ICB, domestic tender, shopping, sole source.
    start_date = db.Column(db.Date, nullable=False) # This is the first day that the procurement price is valid for (may be left blank).
    end_date = db.Column(db.Date, nullable=True) # This is the last day that the procurement price is valid for (may be left blank).
    incoterm = db.Column(db.String(3), nullable=True)  # The international trade term applicable to the contracted price. Ideally this should be standardised as FOB or EXW to allow comparability.
    added_on = db.Column(db.Date, default=datetime.datetime.today())
    approved = db.Column(db.Boolean, default=False)

    currency_id = db.Column(db.Integer, db.ForeignKey('currency.currency_id'), nullable=False)
    currency = db.relationship('Currency', backref='procurements')
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    product = db.relationship('Product', backref='procurements', lazy='joined')
    incoterm_id = db.Column(db.Integer, db.ForeignKey('incoterm.incoterm_id'), nullable=True)
    incoterm = db.relationship('Incoterm')
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'), nullable=True)
    country = db.relationship('Country', lazy='joined')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'), nullable=True)
    supplier = db.relationship('Supplier', backref='procurements')
    source_id = db.Column(db.Integer, db.ForeignKey('source.source_id'), nullable=True)
    source = db.relationship('Source')
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    added_by = db.relationship('User', foreign_keys=added_by_id, backref='procurements_added')
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    approved_by = db.relationship('User', foreign_keys=approved_by_id, backref='procurements_approved')

    def __unicode__(self):
        if self.quantity:
            return u'%d x %s' % (self.quantity, self.product.__unicode__())
        return u'unknown quantity x %s' % (self.product.__unicode__())

    def to_dict(self, include_related=False):
        return serializers.procurement_to_dict(self, include_related)


class AvailableContainers(db.Model):

    __tablename__ = "available_containers"

    available_container_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), unique=True, nullable=False)

    def __unicode__(self):
        return u'%s' % self.value

    def __repr__(self):
        return self.__unicode__()


class UnitOfMeasure(db.Model):

    __tablename__ = "unit_of_measure"

    unit_of_measure_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(32), unique=True, nullable=False)

    def __unicode__(self):
        return u'%s' % self.value


class AvailableProcurementMethods(db.Model):

    __tablename__ = "available_procurement_methods"

    available_procurement_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), unique=True, nullable=False)

    def __unicode__(self):
        return u'%s' % self.value