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
    return values[index]

def phone(value):
    if not value:
        return value
    number = re.sub(r'[^0-9()]+', '', unicode(value).split(',')[0])
    return number
    
def update_supplier(values):
    suppliers = models.Supplier.objects.filter(name=values['name'])
    if suppliers.count() == 0:
        supplier = models.Supplier()
        print 'CREATE: %s' % values['name']
    elif suppliers.count() == 1:
        supplier = suppliers[0]
        print 'UPDATE: %s' % values['name']
    else:
        print 'ERROR: Multiple suppliers match name. Not updated. (%s)' % values['name']
        return
    supplier.name = values['name']
    supplier.address = values['address']
    country, _ = models.Country.objects.get_or_create(name=values['country'])
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


def convert(filename):
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(0)
    suppliers = []
    headings = [alnum(h) for h in sh.row_values(0)]
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
    return

if __name__=='__main__':
    filename = sys.argv[1]
    with transaction.commit_on_success():
        data = convert(filename)
    print('Operation completed succesfully.')
        
