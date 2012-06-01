#!/usr/bin/env python

import sys
import xlrd
import json
from datetime import datetime

from registrations import models
from django.db.models import Count

DEBUG = True
USD_ZAR = 8.42113

class ValidationError(ValueError):
    pass

class ImportError(ValueError):
    pass

def validate(filename):
    EXPECTED = { (0,0): 'Database Of Medicine Prices',
                 (1,0): 'Applicants MCC Licence No',
                 (1,1): 'Applicant Name',
                 (1,2): 'Product MCC Registration No',
                 (1,3): 'Nappi Code',
                 (1,4): 'ATC 4 ',
                 (1,5): 'Schedule',
                 (1,6): 'Product Proprietary Name',
                 (1,7): 'Active Ingredients',
                 (1,8): 'Strength',
                 (1,9): 'Unit',
                 (1,10): 'Pack Size',
                 (1,11): 'Dosage Form',
                 (1,12): 'Manufacturer Price',
                 (1,13): 'Logistics Fee',
                 (1,14): 'VAT',
                 (1,15): 'SEP',
                 (1,16): 'Unit Price',
                 (1,17): 'Effective Date',
                 (1,18): 'Status' }
    wb = xlrd.open_workbook(filename)
    if 'Database Of Medicine Prices' not in wb.sheet_names():
        raise ValidationError('Expected sheet called `Database Of Medicine Prices` but it does not exist.')
    sh = wb.sheet_by_name(u'Database Of Medicine Prices')
    for cell, value in EXPECTED.items():
        if sh.cell(cell[0], cell[1]).value != value:
            raise ValidationError('Unexpected value in cell %d,%d. Expected `%s`, got `%s`.' % (cell[0], cell[1], value, sh.cell(cell[0], cell[1]).value))

s_obj = None
def source():
    # Create a source.
    global s_obj
    if not s_obj:
        s_obj = models.Source()
        s_obj.name = 'South Africa Single Exit Price database importer.'
        s_obj.date = datetime.now()
        s_obj.save()
    return s_obj

c_obj = None
def country():
    global c_obj
    if not c_obj:
        c_obj, created = models.Country.objects.get_or_create(name='South Africa', code='za')
    return c_obj

i_obj = None
def incoterm():
    global i_obj
    if not i_obj:
        i_obj, created = models.Incoterm.objects.get_or_create(name='UNK', description='Unknown Incoterm')
    return i_obj
    
def add_medicine(m):
    # Create the supplier.
    try:
        supplier = models.Supplier.objects.get(name=m['supplier'])
    except models.Supplier.DoesNotExist:
        supplier = models.Supplier()
        supplier.name = m['supplier']
        supplier.source = source()
        supplier.save()
        if DEBUG: print('Created supplier: %s' % (m['supplier'].encode('ascii', 'ignore')))
    # Create the medicine for this item.
    medicines = models.Medicine.objects.all()
    medicines = medicines.annotate(num_i=Count('ingredient')).filter(num_i=len(m['ingredients']))
    for i in m['ingredients']:
        medicines = medicines.filter(ingredient__inn__name=i['inn'],
                                     ingredient__strength=i['strength'] )
    count = medicines.count()
    if count == 0:
        dosageform, created = models.DosageForm.objects.get_or_create(name=m['dosageform'])
        if created:
            if DEBUG: print('Created dosage form: %s' % (m['dosageform'].encode('ascii', 'ignore')))
        medicine = models.Medicine()
        medicine.source = source()
        medicine.dosageform = dosageform
        medicine.save()
        for i in m['ingredients']:
            inn, created = models.INN.objects.get_or_create(name=i['inn'])
            if created:
                if DEBUG: print('Created INN: %s' % (i['inn'].encode('ascii', 'ignore')))
            ingredient = models.Ingredient()
            ingredient.medicine = medicine
            ingredient.inn = inn
            ingredient.strength = i['strength']
            ingredient.save()
    elif count == 1:
        medicine = medicines[0]
    else:
        print(medicines)
        raise ImportError('Multiple medicines match ingredient set.')
    # Create the product for the item.
    products = models.Product.objects.filter(name=m['name'], medicine=medicine)
    count = products.count()
    if count == 0:
        product = models.Product()
        product.name = m['name']
        product.medicine = medicine
        product.source = source()
        product.save()
        if DEBUG: print('Created product: %s' % (m['name'].encode('ascii', 'ignore')))
    elif count == 1:
        product = products[0]
    else:
        print(products)
        raise ImportError('Multiple products match entry.')
    # Create registration for the item.
    registrations = models.Registration.objects.filter(number=m['registration'])
    count = registrations.count()
    if count == 0:
        registration = models.Registration()
        registration.source = source()
        registration.number = m['registration']
        registration.country = country()
        registration.supplier = supplier
        registration.product = product
        registration.save()
        if DEBUG: print('Created registration %s.' % (m['registration']))
    elif count == 1:
        registration = registrations[0]
    else:
        print(registrations)
        raise ImportError('Multiple registrations match number.')
    if m.has_key('packsize'):
        packsizes = models.PackSize.objects.filter(registration=registration,
                                                   quantity=m['packsize'])
        count = packsizes.count()
        if count == 0:
            packsize = models.PackSize()
            packsize.registration = registration
            packsize.quantity = m['packsize']
            packsize.save()
            if DEBUG: print('Created packsize %d.' % (m['packsize']))
        elif count == 1:
            packsize = packsizes[0]
        else:
            print('Warning: Duplicate packsizes found for %s.' % (m['name']))
    else:
        packsize = None
    # Create procurement object for the item.
    procurements = models.Procurement.objects.filter(country=country())
    procurements = procurements.filter(product=product)
    if packsize:
        procurements = procurements.filter(pack=packsize)
    procurements = procurements.filter(incoterm=incoterm())
    if m.has_key('date'):
       procurements  = procurements.filter(validity=m['date'])
    count = procurements.count()
    if count == 0:
        procurement = models.Procurement()
        procurement.source = source()
        procurement.country = country()
        procurement.supplier = supplier
        procurement.product = product
        procurement.pack = packsize
        if m.has_key('date'):
            procurement.validity = m['date']
        procurement.incoterm = incoterm()
        if m.has_key('price'):
            procurement.price = m['unitprice']
        else:
            procurement.price = 0
        procurement.save()
        if DEBUG: print('Created procurement for %s.' % (m['name'].encode('ascii','ignore')))
    elif count == 1:
        procurement = procurements[0]
    else:
        print('Warning: Multiple similar procurements found for %s.' % (m['name']))
    

def convert(filename):
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_name(u'Database Of Medicine Prices')
    medicine_list = []
    medicine = None
    for row in range(2,sh.nrows):
        if row%100 == 0:
            print('Processing row %d.' % (row))
        values = sh.row_values(row)
        if values[1]:
            if medicine:
                add_medicine(medicine)
                medicine_list.append(medicine)
            medicine = { 'name': values[6].strip(),
                         'ingredients': [],
                         'supplier': values[1].strip(),
                         'registration': values[2].strip(),
                         'dosageform': values[11].strip() }
            if values[3]:
                medicine['nappi'] = int(values[3])
            if values[10]:
                medicine['packsize'] = int(values[10])
            if values[12] and values[10]:
                medicine['unitprice'] = (values[12]/USD_ZAR)/values[10]
            if values[17]:
                date = xlrd.xldate_as_tuple(values[17], wb.datemode)
                medicine['date'] = datetime(*date).strftime('%Y-%m-%d')
        # Some entries contain duplicate ingredients. Stupid.
        strength = '%g%s' % (values[8] or 0, values[9])
        found = False
        for i in medicine['ingredients']:
            if (i['inn'] == values[7].lower().strip() and
                i['strength'] == strength):
                found = True
                print('Warning: Duplicate ingredient encountered. Ignoring.')
        if not found:
            medicine['ingredients'].append({ 'inn': values[7].lower().strip(),
                                             'strength': strength })
    return medicine_list


if __name__=='__main__':
    filename = sys.argv[1]
    try:
        validate(filename)
    except ValidationError, e:
        print('Validation failed:\n%s' % (e))
    else:
        data = convert(filename)
        #print(json.dumps(data, indent=2))
        print('Operation completed succesfully.')
        
