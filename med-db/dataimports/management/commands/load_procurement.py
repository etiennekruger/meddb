import csv
import sys

from django.core.management.base import BaseCommand, CommandError
import registrations.models as rmodels
from fuzzywuzzy import process

def match_medicines(data, callback, processor=lambda x : x):
    for m in rmodels.Medicine.objects.all():
        print "Candidate: ", m, m.actives, m.dosageform
        print "=" * 30
        print ""
        candidates = process.extract(m.name + " " + str(m.dosageform), data, processor, limit=15)
        for idx, (c, score) in enumerate(candidates):
            print "%d) %s - %s" % (idx, processor(c), score)
        print "-1) No of the above"
        input = int(raw_input())

        if input >= 0:
            c = candidates[input][0]
            callback(m, c)
        else:
            callback(m, None)
        print "=" * 30
        print ""

def match_or_create_manufacturer(manufacturer):
    try:
        manufacturer = rmodels.Manufacturer.objects.get(
            name=manufacturer.name,
            country=manufacturer.country
        )
    except rmodels.Manufacturer.DoesNotExist:
        manufacturer.save()
    return manufacturer

def match_or_create_supplier(supplier):
    if type(supplier) == rmodels.Manufacturer:
        supplier, _ = rmodels.Supplier.objects.get_or_create(
            name=supplier.name,
            manufacturer=supplier
        )
        return supplier
    else:
        supplier, _ = rmodels.Supplier.objects.get_or_create(
            name=supplier
        )
        return supplier

def match_or_create_product(medicine, manufacturer, product_name):
    try:
        return rmodels.Product.objects.get(medicine=medicine, manufacturer=manufacturer)
    except rmodels.Product.DoesNotExist:
        return rmodels.Product.objects.create(
            medicine=medicine,
            manufacturer=manufacturer,
            name=product_name
        )


class Command(BaseCommand):

    def handle_match(self, medicine, match):
        try:
            if not match:
                return

            if not "Procuring Country" in match:
                sys.stderr.write("Procuring country expected - skipping row: %s\n" % match)
                return
            procuring_country, _ = rmodels.Country.objects.get_or_create(name=match["Procuring Country"])
                
            m = rmodels.Manufacturer()

            if "Manufacturer" in match:
                m.name = match["Manufacturer"]
                if match["Manufacturer Country"]:
                    country, _ = rmodels.Country.objects.get_or_create(name=match["Manufacturer Country"])
                else:
                    country = None
                m.country = country

                if "Manufacturer Website" in match:
                    m.website = match["Manufacturer Country"]
                
                manufacturer = match_or_create_manufacturer(m)
            else:
                manufacturer = None

            if "Supplier" in match and match["Supplier"]:
                supplier = match_or_create_supplier(match["Supplier"])
            elif manufacturer:
                supplier = match_or_create_supplier(m)
            else:
                supplier = None
            product_name = match["Product"] if "Product" in match else match["Description"]
            product = match_or_create_product(medicine, manufacturer, product_name)
            incoterm, _ = rmodels.Incoterm.objects.get_or_create(name=match["Incoterm"] if ("Incoterm" in match and match["Incoterm"]) else "Unknown")

            procurement = rmodels.Procurement.objects.create(
               country=procuring_country,
               product=product,
               supplier=supplier,
               incoterm=incoterm,
               price=float(match["Unit Price"]),
               source=self.source
            )

            print "%s matches %s" % (medicine, match)
        except (TypeError, ValueError):
            import traceback
            traceback.print_exc()
            return

    def handle(self, *args, **options):
        r = csv.reader(open(args[0]))
        headers = r.next()
        data = []
        for row in r:
            row = [None if r == "" else r.strip() for r in row]
            datum = dict(zip(headers, row))
            data.append(datum)
            
        print "Give this source a name - e.g. Seychelles Procurement List (2012-05-19)"
        source_name = raw_input()
        self.source = rmodels.Source.objects.create(name=source_name)
        match_medicines(data, self.handle_match, processor=lambda x : x["Description"])
