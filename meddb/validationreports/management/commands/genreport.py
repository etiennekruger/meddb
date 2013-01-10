import csv
import sys
from django.core.management.base import BaseCommand, CommandError
from registrations import models as rmodels

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
            "volume",
            "correct (please mark with Y for yes and N for no",
        ]
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        for procurement in procurements:
            writer.writerow(procurement)

    def getprocurements(self, country):
        for procurement in rmodels.Procurement.objects.filter(country__name=country):
            yield [
                procurement.start_date,
                procurement.end_date,
                procurement.product.medicine,
                procurement.product.name,
                procurement.product.manufacturer,
                procurement.product.site,
                procurement.pack.pack,
                procurement.pack.quantity,
                procurement.supplier,
                procurement.incoterm,
                procurement.price,
                procurement.volume,
            ]
