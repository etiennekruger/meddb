from django.db import models
from django.core.urlresolvers import reverse
import datetime

# Abstract base models.
#
# These are base models for other complex models to derive off.

class Source(models.Model):
    name = models.CharField(max_length=64)
    date = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return u'%s @ %s' % (self.name, self.date)

class SourcedModel(models.Model):
    source = models.ForeignKey(Source)

    class Meta:
        abstract = True

# Basic models.
#
# These are the basic general purpose models with no link to other models or to a
# source of information. Other models may link back to these.

class Country(models.Model):
    name = models.CharField(max_length=16)
    code = models.CharField(max_length=2)
    
    def as_dict(self, minimal=False):
        return { 'id': self.id,
                 'name': self.name,
                 'code': self.code }
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code.upper())

    class Meta:
        verbose_name_plural = 'Countries'

class Incoterm(models.Model):
    name = models.CharField(max_length=3)
    description = models.CharField(max_length=128)
    
    def as_dict(self, minimal=False):
        return self.name
    
    def __unicode__(self):
        return u'%s' % (self.name)

class DosageForm(models.Model):
    name = models.CharField(max_length=16)
    
    def as_dict(self, minimal=False):
        return self.name
    
    def __unicode__(self):
        return u'%s' % (self.name)

class INN(models.Model):
    name = models.CharField(max_length=128)
    
    def as_dict(self, minimal=False):
        d = { 'id': self.id,
              'name': self.name }
        if not minimal:
            d['medicines'] = [m.as_dict(minimal=True) for m in self.medicine_set.all()]
        return d
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    class Meta:
        verbose_name = 'INN'
        verbose_name_plural = 'INN\'s'

# Generic product models.
#
# These models will represent a generic product including all it's active ingredients,
# their strength and the dosage form of the product.

class Medicine(SourcedModel):
    ingredients = models.ManyToManyField(INN, through='Ingredient')
    dosageform = models.ForeignKey(DosageForm)
    
    @property
    def actives(self):
        return ', '.join([str(i) for i in self.ingredient_set.all()])
    
    def as_dict(self, products=True, minimal=False):
        d = { 'id': self.id,
              'ingredients': [i.as_dict() for i in self.ingredient_set.all()],
              'dosageform': self.dosageform.as_dict() }
        if products:
            d['products'] = [p.as_dict(medicine=False, minimal=minimal) for p in self.product_set.all()]
        return d
    
    def __unicode__(self):
        return u'%s %s' % (self.actives, self.dosageform)

class Ingredient(models.Model):
    medicine = models.ForeignKey(Medicine)
    inn = models.ForeignKey(INN)
    strength = models.CharField(max_length=16)
    
    def as_dict(self, minimal=False):
        return { 'id': self.inn.id,
                 'inn': self.inn.name,
                 'strength': self.strength }
        
    def __unicode__(self):
        return u'%s %s' % (self.inn, self.strength)

class Product(SourcedModel):
    name = models.CharField(max_length=64)
    medicine = models.ForeignKey(Medicine)
    
    def as_dict(self, medicine=True, minimal=False):
        d = { 'id': self.id,
              'name': self.name }
        if medicine:
            d['medicine'] = self.medicine.as_dict(minimal=True, products=False)
        if not minimal:
            d['registrations'] = [r.as_dict(minimal=True, medicine=False) for r in self.registration_set.all()]
        return d
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, str(self.medicine))

# Manufacturer information.
#
# These models represent the manufacturers and their manufacturing sites.

class Manufacturer(SourcedModel):
    name = models.CharField(max_length=64, verbose_name='Manufacturer Name')
    country = models.ForeignKey(Country, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    def as_dict(self, minimal=False):
        d = { 'id': self.id,
              'name': self.name,
              'country': self.country.as_dict(),
              'website': self.website }
        if not minimal:
            d['sites'] = [s.as_dict(minimal=True) for s in self.site_set.all()]
            d['suppliers'] = [s.as_dict(minimal=True, manufacturer=False) for s in self.supplier_set.all()]
        return d
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.country.code.upper())

class Site(SourcedModel):
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(max_length=64, verbose_name='Site Name')
    address = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=64, verbose_name='Contact Person', blank=True, null=True)
    phone = models.CharField(max_length=16, verbose_name='Phone Number', blank=True, null=True)
    altphone = models.CharField(max_length=16, verbose_name='Alternative Phone Number', blank=True, null=True)
    fax = models.CharField(max_length=16, verbose_name='Fax Number', blank=True, null=True)
    email = models.EmailField(verbose_name='Email Address', blank=True, null=True)
    altemail = models.EmailField(verbose_name='Alternative Email Address')
    prequalify = models.BooleanField(verbose_name='NMPA Pre-qualified')
    
    def as_dict(self, minimal=False):
        d = { 'id': self.id,
              'name': self.name,
              'country': self.country.as_dict(),
              'website': self.website,
              'contact': self.contact,
              'phone': self.phone,
              'fax': self.fax,
              'email': self.email,
              'prequalify': self.prequalify }
        if not minimal:
            d.update({ 'address': self.address,
                       'altphone': self.altphone,
                       'altemail': self.altemail })
            d['registrations'] = [r.as_dict(minimal=True) for r in Registration.objects.all()]
            d['procurements'] = [p.as_dict(minimal=True) for p in Procurement.objects.all()]
            d['manufacturer'] = self.manufacturer.as_dict(minimal=True)
        return d
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.manufacturer.name)
    
    class Meta:
        verbose_name = 'Manufacturing Site'

class Supplier(SourcedModel):
    name = models.CharField(max_length=64)
    address = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=64, verbose_name='Contact Person', blank=True, null=True)
    phone = models.CharField(max_length=16, verbose_name='Phone Number', blank=True, null=True)
    altphone = models.CharField(max_length=16, verbose_name='Alternative Phone Number', blank=True, null=True)
    fax = models.CharField(max_length=16, verbose_name='Fax Number', blank=True, null=True)
    email = models.EmailField(verbose_name='Email Address', blank=True, null=True)
    altemail = models.EmailField(verbose_name='Alternative Email Address', blank=True, null=True)
    prequalify = models.BooleanField(verbose_name='NMPA Pre-qualified', default=False)
    authorized = models.BooleanField(verbose_name='Manufacturer Authorisation', default=False)
    
    def is_manufacturer(self):
        if not self.manufacturer:
            return False
        return True
    
    def as_dict(self, minimal=False, manufacturer=True):
        d = { 'id': self.id,
              'name': self.name,
              'website': self.website,
              'contact': self.contact,
              'phone': self.phone,
              'fax': self.fax,
              'email': self.email,
              'prequalify': self.prequalify,
              'authorized': self.authorized }
        if self.country:
              d['country'] = self.country.as_dict()
        if manufacturer:
            if self.manufacturer:
                d['manufacturer'] = self.manufacturer.as_dict(minimal=True)
        if not minimal:
            d.update({ 'address': self.address,
                       'altphone': self.altphone,
                       'altemail': self.altemail })
            d['registrations'] = [r.as_dict(minimal=True) for r in self.registration_set.all()]
            d['procurements'] = [p.as_dict(minimal=True) for p in self.procurement_set.all()]
        return d
    
    def __unicode__(self):
        return u'%s' % (self.name)

# Registration information.
#
# These models will represent actual registrations of products.

class Pack(models.Model):
    name = models.CharField(max_length=32)
    
    def as_dict(self, minimal=False):
        return self.name
    
    def __unicode__(self):
        return u'%s' % (self.name)

class PackSize(models.Model):
    pack = models.ForeignKey(Pack, blank=True, null=True)
    registration = models.ForeignKey('Registration')
    quantity = models.IntegerField()
    
    def as_dict(self, minimal=False):
        d = { 'quantity': self.quantity }
        if self.pack:
            d['id'] = self.pack.id
            d['name'] = self.pack.name
        return d
    
    def __unicode__(self):
        if self.pack:
            return u'%s (%s)' % (self.pack.name, self.quantity)
        return u'unknown (%s)' % (self.quantity)

class Registration(SourcedModel):
    country = models.ForeignKey(Country)
    number = models.CharField(max_length=32)
    product = models.ForeignKey(Product)
    packs = models.ManyToManyField(Pack, through='PackSize')
    manufacturer = models.ForeignKey(Site, verbose_name='Manufacturer Site', blank=True, null=True)
    supplier = models.ForeignKey(Supplier, blank=True, null=True)
    status = models.BooleanField(default=True)
    application = models.DateField(verbose_name='Application Date', blank=True, null=True)
    registered = models.DateField(verbose_name='Registration Date', blank=True, null=True)
    expiry = models.DateField(verbose_name='Registration Expiry Date', blank=True, null=True)
    
    def as_dict(self, minimal=False, medicine=True):
        d = { 'id': self.id,
              'number': self.number,
              'country': self.country.as_dict(),
              'packs': [p.as_dict() for p in self.packsize_set.all()],
              'status': self.status }
        d['product'] = self.product.as_dict(minimal=True, medicine=medicine)
        if self.application:
            d['application'] = self.application.isoformat()
        if self.registered:
            d['registered'] = self.registered.isoformat()
        if self.expiry:
            d['expiry'] = self.expiry.isoformat()
        if not minimal:
            if self.manufacturer:
                d['site'] = self.manufacturer.as_dict(minimal=True)
            if self.supplier:
                d['supplier'] = self.supplier.as_dict(minimal=True)
        return d
    
    def __unicode__(self):
        return u'%s - %s' % (self.number, self.product.name)

# Procurement information.
#
# Models for the procurement information.

class Procurement(SourcedModel):
    country = models.ForeignKey(Country)
    product = models.ForeignKey(Product)
    pack = models.ForeignKey(PackSize, blank=True, null=True)
    site = models.ForeignKey(Site, verbose_name='Manufacturer Site', blank=True, null=True)
    supplier = models.ForeignKey(Supplier, blank=True, null=True)
    incoterm = models.ForeignKey(Incoterm, help_text='The international trade term applicable to the contracted price. Ideally this should be standardised as FOB or EXW to allow comparability.')
    price = models.FloatField(verbose_name='Price per Pack (USD)')
    volume = models.IntegerField(help_text='The number of packs contracted at the specified unit price.', blank=True, null=True)
    period = models.IntegerField(max_length=16, verbose_name='Procurement Period', help_text='Time frame in months during which the contract will be implemented.', blank=True, null=True)
    method = models.CharField(max_length=32, verbose_name='Procurement Method', help_text='Open or restricted ICB, domestic tender, shopping, sole source.', blank=True, null=True)
    validity = models.DateField(max_length=32, verbose_name='Validity Period', help_text='This describes the date that the procurement price is valid at.', blank=True, null=True)
    
    def as_dict(self, site=True, supplier=True, product=True, minimal=False):
        d = { 'id': self.id,
              'incoterm': self.incoterm.as_dict(),
              'price': self.price,
              'volume': self.volume,
              'period': self.period,
              'method': self.method,
              'country': self.country.as_dict() }
        if self.validity:
            d['validity'] = self.validity.isoformat()
        if self.pack:
              d['pack'] = self.pack.as_dict()
        if not minimal:
            if site and self.site:
                d['site'] = self.site.as_dict(minimal=True)
            if supplier and self.supplier:
                d['supplier'] = self.supplier.as_dict(minimal=True)
        if product:
            d['product'] = self.product.as_dict(minimal=minimal)
        return d
    
    def __unicode__(self):
        if self.volume:
            return u'%d x %s' % (self.volume, self.product.name)
        return u'unknown quantity x %s' % (self.product.name)

# Contextual information.
#
# Models representing the contextual information for a source.

class Context(SourcedModel):
    country = models.ForeignKey(Country)
    population = models.IntegerField(blank=True, null=True)
    gni_per_capita = models.FloatField(verbose_name='GNI per capita', blank=True, null=True)
    nmra_name = models.CharField(max_length=32, verbose_name='NMRA Name', blank=True, null=True)
    nmra_website = models.URLField(verbose_name='NMRA Name', blank=True, null=True)
    pspa_name = models.CharField(max_length=32, verbose_name='PSPA Name', blank=True, null=True)
    pspa_website = models.URLField(verbose_name='PSPA Name', blank=True, null=True)
    nmpa_name = models.CharField(max_length=32, verbose_name='NMPA Name', blank=True, null=True)
    nmpa_website = models.URLField(verbose_name='NMPA Name', blank=True, null=True)
    nmpa_status = models.CharField(max_length=32, help_text='e.g. MOH department, public company, NGO.', blank=True, null=True)
    budget = models.FloatField(verbose_name='Annual public sector pharmaceutical procurement budget (USD)', help_text='Including all relevant on-budget budget lines (e.g. including vertical programmes, NMPA, districts, hospitals as adequate).', blank=True, null=True)
    tender_time = models.IntegerField(help_text='Number of months from selection and quantification up to contract award; for open or restricted ICB only.', blank=True, null=True)
    tender_currencies = models.CharField(max_length=32, blank=True, null=True)
    payment_terms = models.CharField(max_length=32, verbose_name='Payment terms/modalities', help_text='e.g. Letter of Credit, other forms of pre-payment against performance guarantee, on account (XX days).', blank=True, null=True)
    local_preference = models.CharField(max_length=64, help_text='% figure and requirements applicable to local preference.', blank=True, null=True)
    import_duty = models.FloatField(max_length=64, verbose_name='Import duties and taxes', help_text='% figure as applicable.', blank=True, null=True)
    freight = models.FloatField(max_length=64, verbose_name='Average cost for freight & insurance', help_text='% figure.', blank=True, null=True)
    
    def as_dict(self, minimal=False):
        d = {}
        return d
    
    def __unicode__(self):
        return u'%d x %s' % (self.volume, self.product.name)
