#!/usr/bin/env python

import sys
import xlrd
import json
import re
from pprint import pprint
from datetime import datetime
from django.db import transaction

from registrations import models
from django.db.models import Count

DEBUG = False
USD_ZAR = 8.42113

class ValidationError(ValueError):
    pass

class ImportError(ValueError):
    pass

def get_medicines(inn, strength, dosageform):
    assert(type(inn)==list)
    assert(type(strength)==list)
    ingredients = zip(inn, strength)
    # Filter on number of ingredients.
    query = models.Medicine.objects.annotate(count=Count('ingredient')).filter(count=len(ingredients))
    query = query.filter(dosageform__name=dosageform)
    # And now filter on every ingredient.
    for inn, strength in ingredients:
        query = query.filter(ingredient__inn__name=inn, ingredient__strength=strength)
    return query

def alnum(text):
    return re.sub(r'[\W_]+', '', text.strip().lower())
    
def grab(values, headings, title):
    try:
        index = headings.index(title)
    except ValueError:
        return None
    if (hasattr(values[index], 'lower') and
        values[index].lower() == 'n/a'):
        return None
    if hasattr(values[index], 'strip'):
        return values[index].strip()
    return values[index]

def phone(value):
    if not value:
        return value
    number = re.sub(r'[^0-9()]+', '', unicode(value).split(',')[0])
    return number

def date(value, wb):
    try:
        d = xlrd.xldate_as_tuple(value, wb.datemode) 
        return datetime(*d).strftime('%Y-%m-%d')
    except:
        return None

def boolean(value):
    if hasattr(value, 'lower'):
        if value.lower() in ['yes', 'y', 'true']:
            return True
    elif type(value) == int or type(value) == float:
        return value > 0
    return False

def separate(value):
    value = unicode(value)
    if not value:
        return []
    items = [i.strip() for i in value.split('+')]
    return items

def lower(value):
    try:
        return value.lower()
    except:
        return value
    
def update_supplier(values):
    try:
        country, _ = models.Country.objects.get_or_create(name=values['country'])
    except:
        return
    suppliers = models.Supplier.objects.filter(name=values['name'], country=country)
    if suppliers.count() == 0:
        supplier = models.Supplier()
        print 'CREATE: %s' % values['name']
    elif suppliers.count() == 1:
        supplier = suppliers[0]
        print 'UPDATE: %s' % values['name']
    else:
        print 'ERROR: Multiple suppliers match name and country. Not updated. (%s, %s)' % (values['name'], values['country'])
        return
    supplier.name = values['name']
    supplier.address = values['address']
    supplier.country = country
    supplier.website = values['website']
    supplier.contact = values['contact']
    supplier.phone = values['phone']
    supplier.altphone = values['altphone']
    supplier.fax = values['fax']
    supplier.email = values['email']
    supplier.altemail = values['altemail']
    supplier.prequalify = values['prequalify'] or False
    supplier.authorized = values['authorized'] or False
    try:
        supplier.save()
    except Exception, e:
        print 'ERROR: Unable to save supplier. Not updated. (%s)' % e
        return
    return

def update_source(values):
    sources = models.Source.objects.filter(name=values['name'])
    if sources.count() == 0:
        source = models.Source()
        print 'CREATE: %s' % values['name']
    elif sources.count() == 1:
        source = sources[0]
        print 'UPDATE: %s' % values['name']
    else:
        print 'ERROR: Multiple sources match name. Not updated. (%s)' % (values['name'])
        return
    source.name = values['name']
    source.date = values['date']
    source.url = values['url']
    try:
        source.save()
    except Exception, e:
        print 'ERROR: Unable to save source. Not updated. (%s)' % e
        return
    return

def update_medicine(values):
    medicines = get_medicines(values['inn'], values['strength'], values['dosageform'])
    if medicines.count() == 0:
        medicine = models.Medicine()
        print 'CREATE: %s' % zip(values['inn'], values['strength'])
    elif medicines.count() == 1:
        medicine = medicines[0]
        print 'EXISTS: %s' % zip(values['inn'], values['strength'])
        return
    else:
        print 'ERROR: Multiple medicnes match ingredients. Not updated. (%s)' % (values['name'])
        return
    try:
        dosageform, _ = models.DosageForm.objects.get_or_create(name=values['dosageform'])
    except:
        return
    medicine.name = values['name']
    medicine.dosageform = dosageform
    medicine.save()
    for inn_name, strength in zip(values['inn'], values['strength']):
        inn, _ = models.INN.objects.get_or_create(name=inn_name)
        i = models.Ingredient(medicine=medicine, inn=inn, strength=strength)
        i.save()
    return

def update_product(values):
    try:
        medicines = get_medicines(values['inn'], values['strength'], values['dosageform'])
        assert(medicines.count()==1)
        medicine = medicines[0]
    except:
        print 'ERROR: Medicine not uniquely identifiable. Not updated. (%s)' % values['name']
        return
    products = models.Product.objects.filter(name=values['name'], medicine=medicine)
    if products.count() == 0:
        product = models.Product()
        print 'CREATE: %s' % values['name']
    elif products.count() == 1:
        product = products[0]
        print 'UPDATE: %s' % values['name']
    else:
        print 'ERROR: Multiple sources match name. Not updated. (%s)' % (values['name'])
        return
    product.medicine = medicine
    product.name = values['name']
    try:
        product.save()
    except Exception, e:
        print 'ERROR: Unable to save source. Not updated. (%s)' % e
        return
    return

def update_registration(values):
    if not values['number']:
        return
    source = models.Source.objects.get(name=values['source'])
    country, _ = models.Country.objects.get_or_create(name=values['country'])
    suppliers = models.Supplier.objects.filter(name=values['supplier'])#, country=values['suppliercountry'])
    registrations = models.Registration.objects.filter(number=values['number'], country=country)
    if registrations.count() == 0:
        registration = models.Registration()
        print 'CREATE: %s' % values['number']
    elif registrations.count() == 1:
        registration = registrations[0]
        print 'UPDATE: %s' % values['number']
    else:
        print 'ERROR: Multiple registrations match number and country. Not updated. (%s, %s)' % (values['number'], values['country'])
        return
    try:
        medicines = get_medicines(values['inn'], values['strength'], values['dosageform'])
        assert(medicines.count()==1)
        medicine = medicines[0]
        products = models.Product.objects.filter(name=values['product'], medicine=medicine)
        assert(products.count()==1)
        product = products[0]
    except Exception, e:
        print 'ERROR: Medicine/Product not uniquely identifiable. Not updated. (%s, %s)' % (values['number'], values['country'])
        print e
        print medicines.count(), products.count()
        return
    # This is a problem. We don't have the supplier countries. Use the first one. Wrong.
    suppliers = models.Supplier.objects.filter(name=values['supplier'])#, country=values['suppliercountry'])
    if suppliers.count() == 0:
        print 'WARNING: Unknown supplier. (%s, %s)' % (values['number'], values['country'])
        #return
        supplier = None
    else:
        supplier = suppliers[0]
    registration.source = source
    registration.country = country
    registration.product = product
    registration.supplier = supplier
    registration.number = values['number']
    registration.status = values['status']
    registration.application = values['application']
    registration.registered = values['registered']
    registration.expiry = values['expiry']
    try:
        registration.save()
    except Exception, e:
        print 'ERROR: Unable to save registration. Not updated. (%s)' % e
        return
    return

def convert(filename):
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(0)
    suppliers = []
    headings = [alnum(h) for h in sh.row_values(0)]
    # Suppliers...
    for row in range(1,sh.nrows):
        values = sh.row_values(row)
        supplier = {}
        supplier['name'] = grab(values, headings, 'suppliername')
        supplier['address'] = grab(values, headings, 'supplieraddress')
        supplier['address2'] = grab(values, headings, 'supplieraddress2')
        supplier['country'] = grab(values, headings, 'suppliercountry')
        supplier['website'] = grab(values, headings, 'supplierwebsite')
        supplier['contact'] = grab(values, headings, 'suppliercontact')
        supplier['phone'] = phone(grab(values, headings, 'supplierphone'))
        supplier['altphone'] = phone(grab(values, headings, 'supplierphone2'))
        supplier['fax'] = phone(grab(values, headings, 'supplierfax'))
        supplier['email'] = grab(values, headings, 'supplieremail')
        supplier['altemail'] = grab(values, headings, 'supplieremail2')
        supplier['prequalify'] = grab(values, headings, 'supplierprequalified')
        supplier['authorized'] = grab(values, headings, 'supplierauthorized')
        update_supplier(supplier)
    # Sources...
    for row in range(1,sh.nrows):
        values = sh.row_values(row)
        source = {}
        source['name'] = grab(values, headings, 'sourcename')
        source['date'] = date(grab(values, headings, 'sourcedate'), wb)
        source['url'] = grab(values, headings, 'sourceurl')
        update_source(source)
    # Medicines...
    for row in range(1,sh.nrows):
        values = sh.row_values(row)
        medicine = {}
        medicine['name'] = grab(values, headings, 'medicinename')
        medicine['inn'] = separate(grab(values, headings, 'medicineinn'))
        medicine['strength'] = separate(grab(values, headings, 'medicinestrength'))
        medicine['dosageform'] = lower(grab(values, headings, 'medicinedosageform'))
        update_medicine(medicine)
    # Products...
    for row in range(1,sh.nrows):
        values = sh.row_values(row)
        product = {}
        product['name'] = grab(values, headings, 'productname')
        product['inn'] = separate(grab(values, headings, 'medicineinn'))
        product['strength'] = separate(grab(values, headings, 'medicinestrength'))
        product['dosageform'] = lower(grab(values, headings, 'medicinedosageform'))
        update_product(product)
    # Registrations...
    for row in range(1,sh.nrows):
        values = sh.row_values(row)
        registration = {}
        registration['inn'] = separate(grab(values, headings, 'medicineinn'))
        registration['strength'] = separate(grab(values, headings, 'medicinestrength'))
        registration['dosageform'] = lower(grab(values, headings, 'medicinedosageform'))
        registration['source'] = grab(values, headings, 'sourcename')
        registration['country'] = grab(values, headings, 'registrationcountry')
        registration['number'] = grab(values, headings, 'registrationnumber')
        registration['product'] = grab(values, headings, 'productname')
        registration['supplier'] = grab(values, headings, 'registrationsuppliername')
        registration['supplier'] = grab(values, headings, 'registrationsuppliercountry')
        registration['status'] = boolean(grab(values, headings, 'registrationstatus'))
        registration['application'] = date(grab(values, headings, 'registrationapplicationdate'), wb)
        registration['registered'] = date(grab(values, headings, 'registrationregistereddate'), wb)
        registration['expiry'] = date(grab(values, headings, 'registrationexpirydate'), wb)
        update_registration(registration)
    return

if __name__=='__main__':
    filename = sys.argv[1]
    with transaction.commit_on_success():
        data = convert(filename)
    print('Operation completed succesfully.')
        
