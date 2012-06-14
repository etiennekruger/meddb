#!/usr/bin/env python

import sys
import xlrd
import json
from datetime import datetime
from django.db import transaction

from registrations import models
from django.db.models import Q, Count

DEBUG = False

class ValidationError(ValueError):
    pass

class ImportError(ValueError):
    pass

def load(filename):
    # Open workbook.
    wb = xlrd.open_workbook(filename)
    # Create a source object for these entries.
    source = models.Source()
    source.name = 'EAC Countries data importer. (Lauren\'s files)'
    source.date = datetime.now()
    source.save()
    # Load all sheets - we need to process the data per line.
    product_sh = wb.sheet_by_name(u'Product information')
    supplier_sh = wb.sheet_by_name(u'Supplier information')
    procurement_sh = wb.sheet_by_name(u'Procurement information')
    context_sh = wb.sheet_by_name(u'Contextual information')
    import_country = context_sh.row_values(6)[1]
    # Iterate over all rows and get / create models.
    nrows = min([product_sh.nrows,supplier_sh.nrows,procurement_sh.nrows])
    for row in range(9,nrows):
        values = product_sh.row_values(row)
        if values[1]:
            print values[1]
            # Create a medicine object if it does not exist.
            inn = [i.strip().lower() for i in values[1].split('+')]
            if type(values[2])==unicode:
                strength = [s.strip().lower() for s in values[2].split('+')]
            else:
                strength = ['%g' % (values[2]),]
            dosageform, _ = models.DosageForm.objects.get_or_create(name=values[3])
            medicines = models.Medicine.objects.annotate(num=Count('ingredient')).filter(num=len(inn))
            for item in zip(inn, strength):
                medicines = medicines.filter(ingredient__inn__name=item[0],
                                             ingredient__strength=item[1])
            medicines = medicines.filter(dosageform=dosageform)
            if medicines.count() == 0:
                medicine = models.Medicine()
                medicine.source = source
                medicine.dosageform = dosageform
                medicine.save()
                for item in zip(inn, strength):
                    inn, _ = models.INN.objects.get_or_create(name=item[0])
                    ingredient = models.Ingredient()
                    ingredient.medicine = medicine
                    ingredient.inn = inn
                    ingredient.strength = item[1]
                    ingredient.save()
            elif medicines.count() == 1:
                medicine = medicines[0]
            else:
                raise ImportError('Multiple medicines match ingredient set.')
            # EAC data has no product info. Use dummy data.
            products = models.Product.objects.filter(medicine=medicine)
            if products.count() == 0:
                product = models.Product()
                product.source = source
                product.name = 'Unknown Product'
                product.medicine = medicine
                product.save()
            elif products.count() == 1:
                product = products[0]
            else:
                raise ImportError('Multiple products match ingredient set.')
        # Now for the suppliers...
        values = supplier_sh.row_values(row)
        if values[0]:
            countries = models.Country.objects.filter(name=values[2])
            if countries.count() == 0:
                country = models.Country()
                country.name = values[2]
                country.code = 'xx'
                country.save()
            elif countries.count() == 1:
                country = countries[0]
            else:
                raise ImportError('Multiple countries match country name.')
            suppliers = models.Supplier.objects.filter(name=values[1])
            if suppliers.count() == 0:
                supplier = models.Supplier()
                supplier.source = source
                supplier.name = values[1]
                supplier.country = country
                supplier.save()
            elif suppliers.count() == 1:
                supplier = suppliers[0]
            else:
                raise ImportError('Multiple suppliers match supplier name.')
        # And the procurements.
        values = procurement_sh.row_values(row)
        if values[3]:
            try:
                incoterm = models.Incoterm.objects.get(name=values[3].strip())
            except models.Incoterm.DoesNotExist:
                raise ImportError('No incoterm matches `%s`.' % (values[3].strip()))
            country = models.Country.objects.get(name=import_country)
            procurement = models.Procurement()
            procurement.source = source
            procurement.product = product
            procurement.supplier = supplier
            procurement.country = country
            if values[4]:
                procurement.volume = values[4]
            procurement.price = values[8]
            procurement.incoterm = incoterm
            try:
                procurement.save()
            except:
                print 'Failed to save procurement.'


if __name__=='__main__':
    filename = sys.argv[1]
    with transaction.commit_on_success():
        data = load(filename)
    print('Operation completed succesfully.')
        
