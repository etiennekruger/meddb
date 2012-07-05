from django.core.management.base import BaseCommand, CommandError
from collections import defaultdict
import csv
import sys
import registrations.models as rmodels
import IPython
from fuzzywuzzy import process

proc_headers = ["Buyer or Seller Name", "Pack Price", "Units in Pack", "Unit Price"]

class MSHMed(object):
    def __init__(self, valdict):
        self.__dict__.update(valdict)

    def __hash__(self):
        return hash(self.key)

    @property
    def key(self):
        return self.Name + " " + self.Strength + " " + self.__dict__["Dosage Form"]

    def __cmp__(self, other):
        return  cmp(hash(self), hash(other))

class Command(BaseCommand):

    def msh_median(self, procurements):
        v = [float(el["Unit Price"]) for el in procurements] 
        v.sort()
        l = len(v)
        if l % 2 == 0:
            return (v[l/2 - 1] + v[l/2]) / 2
        else: 
            return  v[l/2]

    def handle(self, *args, **options):
        r = csv.reader(open(args[0]))
        headers = r.next()
        data = {}
        for row in r:
            datum = dict(zip(headers, row))
            med = MSHMed(datum)
            if med.Type == "Buyer":
                if not med in data:
                    data[med] = {
                        "procurements" : []
                    }
                data[med]["procurements"].append({h : datum[h] for h in proc_headers})

        median_prices = {}
        for key in data:
            median = self.msh_median(data[key]["procurements"])
            data[key]["median_price"] = median

        for m in rmodels.Medicine.objects.all():
            if rmodels.MSHPrice.objects.filter(medicine=m).count() > 0:
                continue
            print "Candidate: ", m, m.actives, m.dosageform
            print "=" * 30
            print ""
            candidates = process.extract(m.name + " " + str(m.dosageform), data.keys(), processor=lambda x : x.key, limit=15)
            for idx, (c, score) in enumerate(candidates):
                print "%d) %s - %s" % (idx, c.key, score)
            print "-1) No of the above"
            input = int(raw_input())
            if input >= 0:
                med = candidates[input][0]
                c = data[med]
                
                rmodels.MSHPrice.objects.create(
                    medicine=m,
                    price=c["median_price"]
                )
            else:
                print "No match found"
            print "=" * 30
            print ""

            
