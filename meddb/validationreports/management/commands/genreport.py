import csv
import sys
from django.core.management.base import BaseCommand, CommandError
from registrations import models as rmodels
import math

def _r(x):
    if math.floor(x) == int(x):
        return int(x)
    return x

class Command(BaseCommand):
    args = "country"
    help = "generates a validation report for the given country"

    def handle(self, *args, **kwargs):
        country = args[0] 
        procurements = self.getprocurements(country)
        headers = [
            "start_date",
            "end_date",
            "medicine",
            "product name",
            "manufacturer",
            "manufacturing site",
            "pack type",
            "pack size",
            "supplier",
            "incoterm",
            "price",
            "currency",
            "volume",
            "correct (please mark with Y for yes and N for no",
            "comments",
        ]
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        for procurement in procurements:
            writer.writerow(procurement)

    def getprocurements(self, country):
        for procurement in rmodels.Procurement.objects.filter(country__name=country):
            def none_as_blank(procurement, el):
                try:
                    return str(eval(el, globals(), locals()))
                except AttributeError:
                    return ""
        
            if procurement.start_date.year >= 2011:
                yield [
                    none_as_blank(procurement, "procurement.start_date"),
                    none_as_blank(procurement, "procurement.end_date"),
                    none_as_blank(procurement, "procurement.product.medicine"),
                    none_as_blank(procurement, "procurement.product.name"),
                    none_as_blank(procurement, "procurement.product.manufacturer"),
                    none_as_blank(procurement, "procurement.product.site.address"),
                    none_as_blank(procurement, "procurement.container.type + ' (' + str(_r(procurement.container.quantity)) + ' ' + procurement.container.unit + ')'"),
                    none_as_blank(procurement, "procurement.packsize"),
                    none_as_blank(procurement, "procurement.supplier"),
                    none_as_blank(procurement, "procurement.incoterm"),
                    none_as_blank(procurement, "procurement.price"),
                    none_as_blank(procurement, "procurement.currency.code"),
                    none_as_blank(procurement, "procurement.volume"),
                ]
