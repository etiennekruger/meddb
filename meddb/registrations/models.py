from django.db import models
from django.core.urlresolvers import reverse
import currency.models
import datetime

def avg(list):
    if len(list) == 0:
        return float(0)
    return sum(list) / len(list)

# Abstract base models.
#
# These are base models for other complex models to derive off.

class Source(models.Model):
    name = models.CharField(max_length=64)
    date = models.DateTimeField(default=datetime.datetime.now)
    url = models.URLField(blank=True, null=True, verbose_name='Source Document URL', help_text='Provide a link to the source document for reference purposes. Ideally, load the document into the Infohub CKAN installation at data.medicinesinfohub.net and add the link to the source of the document as an additional resource.')
    
    def __unicode__(self):
        s = u'%s @ %s' % (self.name, self.date)
        return s

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
    code = models.CharField(max_length=3)
    
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
        verbose_name_plural = 'INNs'

# Generic product models.
#
# These models will represent a generic product including all it's active ingredients,
# their strength and the dosage form of the product.

class Medicine(models.Model):
    ingredients = models.ManyToManyField(INN, through='Ingredient')
    dosageform = models.ForeignKey(DosageForm)
    name = models.CharField(max_length=50, null=True, blank=True)
    
    @property
    def actives(self):
        return ', '.join([str(i) for i in self.ingredient_set.all()])
    
    @property
    def msh(self):
        try:
            return self.mshprice.price
        except:
            return None
    
    def as_dict(self, products=True, minimal=False, procurements=True):
        if minimal:
            d = {
                'id': self.id,
                'ingredients': [i.as_dict() for i in self.ingredient_set.all()],
                'dosageform': { 'id': self.dosageform.id,
                                'name': self.dosageform.name },
                'avgprice': self.avgprice(),
                'mshprice': self.msh,
                'products': [{
                        'id': p.id,
                        'name': p.name
                        } for p in self.product_set.all()]
                }
            if self.name:
                d['name'] = self.name.capitalize()
            return d
        d = { 'id': self.id,
              'ingredients': [i.as_dict() for i in self.ingredient_set.all()],
              'dosageform': self.dosageform.as_dict(),
              'mshprice': self.msh }
        if self.name:
            d['name'] = self.name.capitalize()
        if procurements:
            d['procurements'] = [p.as_dict() for p in Procurement.objects.filter(product__medicine=self)]
        if products:
            d['products'] = [p.as_dict(medicine=False, minimal=minimal) for p in self.product_set.all()]
        return d
    
    def avgprice(self):
        sum = 0
        tot = 0
        procurements =  Procurement.objects.filter(product__medicine=self)
        for p in procurements:
            sum += p.price_usd * p.volume
            tot += p.container.quantity * p.volume
        if tot > 0:
            return sum/tot
        return None
    
    def __unicode__(self):
        if self.name:
            return u'%s %s' % (self.name, self.dosageform)
        return u'%s %s' % (self.actives, self.dosageform)

class Ingredient(models.Model):
    medicine = models.ForeignKey(Medicine)
    inn = models.ForeignKey(INN)
    strength = models.CharField(max_length=16)
    
    def as_dict(self, minimal=False):
        return { 'id': self.inn.id,
                 'inn': self.inn.name.capitalize(),
                 'strength': self.strength }
        
    def __unicode__(self):
        return u'%s %s' % (self.inn, self.strength)
    
    class Meta:
        ordering = ('inn__name',)

# Pricing information.
#
# These models will probably be altered at some stage to include alternative
# defined prices per medicine. For now it is a simple MSH price.

class MSHPrice(models.Model):
    medicine = models.OneToOneField(Medicine)
    price = models.FloatField(help_text='The MSH price for the medicine.')
    
    def __unicode__(self):
        return u'%s @ %.4f' % (self.medicine, self.price)

class Manufacturer(models.Model):
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
        return u'%s (%s)' % (self.name, self.country.code.upper() if self.country else "No Country")

class Site(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(max_length=64, verbose_name='Site Name')
    address = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    
    def as_dict(self, minimal=False):
        d = {
            'id': self.id,
            'name': self.name,
            'country': self.country.as_dict(),
        }
        if not minimal:
            d['registrations'] = [r.as_dict(minimal=True) for r in Registration.objects.all()]
            d['procurements'] = [p.as_dict() for p in Procurement.objects.all()]
            d['manufacturer'] = self.manufacturer.as_dict(minimal=True)
        return d
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.manufacturer.name)
    
    class Meta:
        verbose_name = 'Manufacturing Site'

class Supplier(models.Model):
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
            d['procurements'] = [{
                    'id': p.id,
                    'product': {
                        'id': p.product.id,
                        'name': p.product.name,
                        'medicine': {
                            'id': p.product.medicine.id,
                            'dosageform': {
                                'id': p.product.medicine.dosageform.id,
                                'name': p.product.medicine.dosageform.name
                                },
                            'ingredients': [{
                                    'inn': i.inn.name.title(),
                                    'strength': i.strength
                                    } for i in p.product.medicine.ingredient_set.all()]
                            },
                            'pack-size' : p.container.as_dict(minimal=True),
                        },
                    'country': {
                        'id': p.country.id,
                        'name': p.country.name
                        }
                    } for p in self.procurement_set.all()]
            #d['procurements'] = [p.as_dict(minimal=True, supplier=False) for p in self.procurement_set.all()]
        return d
    
    def __unicode__(self):
        return u'%s' % (self.name)

class Product(models.Model):
    name = models.CharField(max_length=64, blank=True)
    medicine = models.ForeignKey(Medicine)
    manufacturer = models.ForeignKey(Manufacturer, null=True)
    site = models.ForeignKey(Site, verbose_name='Manufacturer Site', blank=True, null=True)
    # TODO Need to add manufacturer to as_dict
    
    def as_dict(self, medicine=True, minimal=False, registrations=True):
        d = { 'id': self.id,
              'name': self.name }
        if self.manufacturer:
            d['manufacturer'] = {
                'id': self.manufacturer.id,
                'name': self.manufacturer.name,
                'country': self.manufacturer.country.name,
                'site': self.site.name,
            }
        if medicine:
            d['medicine'] = self.medicine.as_dict(minimal=True, products=False, procurements=False)
        if registrations:
            d['registrations'] = [r.as_dict(medicine=False, product=False) for r in self.registration_set.all()]
        if not minimal:
            d['procurements'] = [r.as_dict() for r in self.procurement_set.all()]
        return d
    
    def __unicode__(self):
        if self.name:
            return u'%s - %s (%s)' % (self.name, self.manufacturer, str(self.medicine))
        return u'%s (%s)' % (self.manufacturer, str(self.medicine))



class Container(models.Model):
    type = models.CharField(max_length=32, verbose_name='Container Type', help_text='This should be the actual type of containter that the medicine is distributed in eg. bottle, blister pack, tube etc.')
    unit = models.CharField(max_length=32, verbose_name='Basic Unit', help_text='This represents the basic unit of measure for this container eg. ml (for a bottled suspension), g (for a tube of ointment) or tablet/capsule (for a bottle of tablets/capsules).', blank=True)
    quantity = models.FloatField(verbose_name='Container size in basic units', help_text='The total container size eg. 100 (for a 100ml bottle), 50 (for a bottle of 50 tablets) or 3.5 (for a 3.5g tube of ointment).')
    
    def as_dict(self, minimal=False):
        d = { 'type': self.type,
              'unit': self.unit,
              'quantity': self.quantity }
        return d
    
    def __unicode__(self):
        return u'%.7g %s %s' % (self.quantity, self.unit, self.type)
    

class Registration(SourcedModel):
    country = models.ForeignKey(Country)
    number = models.CharField(max_length=32)
    product = models.ForeignKey(Product)
    manufacturer = models.ForeignKey(Site, verbose_name='Manufacturer Site', blank=True, null=True)
    supplier = models.ForeignKey(Supplier, blank=True, null=True)
    status = models.BooleanField(default=True)
    application = models.DateField(verbose_name='Application Date', blank=True, null=True)
    registered = models.DateField(verbose_name='Registration Date', blank=True, null=True)
    expiry = models.DateField(verbose_name='Registration Expiry Date', blank=True, null=True)
    
    def as_dict(self, minimal=False, medicine=True, product=True):
        d = { 'id': self.id,
              'number': self.number,
              'country': self.country.as_dict(),
              'status': self.status }
        if product:
            d['product'] = self.product.as_dict(minimal=True, medicine=medicine, registrations=False)
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

class Currency(models.Model):
    code = models.CharField(max_length=3, verbose_name='Currency Code', help_text='Enter the ISO 4217 currency code for the currency. This is a 3 letter code in all capitals eg. USD, ZAR etc.')
    
    def __unicode__(self):
        return self.code
    
    class Meta:
        verbose_name_plural = 'Currencies'

class Procurement(SourcedModel):
    country = models.ForeignKey(Country)
    product = models.ForeignKey(Product)
    container = models.ForeignKey(Container, verbose_name='Container', help_text='Indicate the container that the medication is distributed in eg. 100 ml bottle for a paracetamol suspension.')
    packsize = models.IntegerField(verbose_name='Containers in packaging', help_text='Enter the number of containers in the standard packaging eg. 100 bottles of paracetamol suspension per box.', blank=True, null=True)
    supplier = models.ForeignKey(Supplier, blank=True, null=True)
    incoterm = models.ForeignKey(Incoterm, help_text='The international trade term applicable to the contracted price. Ideally this should be standardised as FOB or EXW to allow comparability.')
    price = models.FloatField(verbose_name='Price per container', help_text='The procurement price should be entered in the currency that the purchase was made in and the currency must be indicated below. Note that a unit will be one unit of the container indicated above (eg. the price of one blister pack with 24 capsules in EUR).')
    currency = models.ForeignKey(Currency, help_text='This is the currency of the procurement price. This field is required to convert units to USD for comparison.')
    volume = models.IntegerField(help_text='The number of containers contracted at the specified unit price.', default=1)
    method = models.CharField(max_length=32, verbose_name='Procurement Method', help_text='Open or restricted ICB, domestic tender, shopping, sole source.', blank=True, null=True)
    start_date = models.DateField(max_length=32, verbose_name='Period Start', help_text='This is the first day that the procurement price is valid for (may be left blank).', blank=True, null=True)
    end_date = models.DateField(max_length=32, verbose_name='Period End', help_text='This is the last day that the procurement price is valid for (may be left blank).', blank=True, null=True)
    
    def as_dict(self):
        d = { 'id': self.id,
              'incoterm': { 'id': self.incoterm.id,
                            'name': self.incoterm.name },
              'price': self.price,
              'currency': { 'id': self.currency.id,
                            'code': self.currency.code },
              'price_usd': self.price_usd,
              'volume': self.volume * (self.packsize or 1),
              'method': self.method,
              'country': { 'id': self.country.id,
                           'code': self.country.code,
                           'name': self.country.name },
              'container': { 'id': self.container.id,
                             'type': self.container.type,
                             'unit': self.container.unit,
                             'quantity': self.container.quantity },
              'packsize': self.packsize }
        #if self.pack:
        #    d['pack'] = self.pack.as_dict()
        if self.price_per_unit:
            d['price_per_unit'] = self.price_per_unit
        if self.product:
            d['product'] = { 'id': self.product.id,
                             'name': self.product.name }
        if self.start_date:
            d['start_date'] = self.start_date.isoformat()
        if self.end_date:
            d['end_date'] = self.end_date.isoformat()
        if self.supplier:
            d['supplier'] = { 'id': self.supplier.id,
                              'name': self.supplier.name }
        if self.product and self.product.manufacturer:
            d['manufacturer'] = {
                'id': self.product.manufacturer.id,
                'name': self.product.manufacturer.name,
            }
            if self.product.manufacturer.country:
                d["manufacturer"]["country"] = self.product.manufacturer.country.name,
        return d
    
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

class CountryMappingCode(models.Model):
    country = models.ForeignKey(Country)
    product = models.ForeignKey(Product)
    code = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s - %s" % (self.country, self.code)
