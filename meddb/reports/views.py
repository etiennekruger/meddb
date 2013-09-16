from django.http import HttpResponse
from registrations import models as reg_models
from datetime import datetime
from collections import defaultdict, OrderedDict
from django import http
import csv
import json

sadc_countries = "ANG BWA COD LES MAW MUS MOZ NAM SEY ZAF SWZ TZA ZMB ZWE".split()

def get_procurements(start_date, end_date):
    return reg_models.Procurement.objects.filter(
        end_date__gte=start_date,
        start_date__lte=end_date
    ).order_by("product__medicine__name")

def medicine_grid(request, year):
    
    class MedicinePrices(object):
        def __init__(self, procurements):
            self.prices = {}
            self.procurements = procurements

        def lowest_price(self, medicine):
            if not medicine in self.prices:
                self.prices[medicine] = self.procurements.medicine(medicine).cheapest()

            return self.prices[medicine]

            
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=prices_%s.csv" % year
    writer = csv.writer(response)

    procurements = reg_models.Procurement.objects.in_year(int(year))
    cache = MedicinePrices(procurements)
    writer.writerow([
        "Medicine", "Country", "Unit Price (USD)", "Volume", 
        "Total Value (USD)", "Lowest Price (USD)", "Potential Savings (USD)"
    ])

    for procurement in procurements:
        unit_price = procurement.price_per_unit
        lowest_price = cache.lowest_price(procurement.product.medicine)
        total_value = unit_price * procurement.volume
        potential_savings = total_value - (procurement.volume * lowest_price)

        writer.writerow([
            procurement.product.medicine, procurement.country, procurement.price_per_unit, 
            procurement.volume, total_value, lowest_price, potential_savings
        ])
    return response

def procurement_list(procurements):
    proclist = OrderedDict()
    for procurement in procurements:
        medicine = procurement.product.medicine
        medprocs = proclist.setdefault(medicine, [])
        medprocs.append(procurement)
    
    return proclist

procurement_countries = [
    "Angola", "Botswana", "DRC", "Lesotho", "Malawi", "Mauritius",
    "Mozambique", "Namibia", "Seychelles", "South Africa", "Swaziland",
    "Tanzania", "Zambia", "Zimbabwe"
]

def countries_per_medicine(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=countries_per_medicine.csv"
    writer = csv.writer(response)

    writer.writerow(["Medicine"] + procurement_countries)
    for med in sorted(reg_models.Medicine.objects.all(), key=lambda x: unicode(x)):
        med_name = unicode(med)
        count = [med_name]
        for country in procurement_countries:
            products = reg_models.Product.objects.filter(
                procurement__country__name=country, medicine=med
            )
            count.append(products.count())
        writer.writerow(count)
    return response

def procurement_export(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=all_procurements.csv"
    writer = csv.writer(response)

    writer.writerow(["Country", "Medicine", "Pack", "Supplier", "Incoterm", "Price (USD) / Unit", "Volume", "Start Date", "End Date"])
    for procurement in reg_models.Procurement.objects.all():
        writer.writerow([
            procurement.country,
            procurement.product.medicine,
            procurement.container,
            procurement.supplier,
            procurement.incoterm,
            procurement.price_per_unit,
            procurement.volume,
            procurement.start_date,
            procurement.end_date
        ])
    
    return response
   
    
