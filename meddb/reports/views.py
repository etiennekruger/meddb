from django.http import HttpResponse
from registrations import models as reg_models
from datetime import datetime
from collections import defaultdict, OrderedDict
import csv

sadc_countries = "ANG BWA COD LES MAW MUS MOZ NAM SEY ZAF SWZ TZA ZMB ZWE".split()

def get_procurements(start_date, end_date):
    return reg_models.Procurement.objects.filter(
        end_date__gte=start_date,
        start_date__lte=end_date
    ).order_by("product__medicine__name")

def medicine_grid(procurements):

    medicine_prices = OrderedDict()

    for procurement in procurements:
        print procurement.product.medicine
        med_in_countries = medicine_prices.setdefault(procurement.product.medicine, defaultdict(int))
        price = med_in_countries[procurement.country] 
        if price == 0:
            med_in_countries[procurement.country] = procurement.price_per_unit
        else:
            med_in_countries[procurement.country] = min(med_in_countries[procurement.country], procurement.price_per_unit)

    return medicine_prices

def procurement_list(procurements):
    proclist = OrderedDict()
    for procurement in procurements:
        medicine = procurement.product.medicine
        medprocs = proclist.setdefault(medicine, [])
        medprocs.append(procurement)
    
    return proclist

def reference_report(request):
    
    def fmt_price(p):
        return ("%.5f" % p) if p else "-"

    fp = open("/tmp/out.csv", "w")
    writer = csv.writer(fp)

    current_year = datetime.now().year
    start_date = datetime.strptime(
        request.GET.get("start_date", "%d-01-01" % current_year),
        "%Y-%m-%d"
    )
    end_date = datetime.strptime(
        request.GET.get("end_date", "%d-12-31" % current_year),
        "%Y-%m-%d"
    )


    procurements = get_procurements(start_date, end_date)
    countries = reg_models.Country.objects.filter(code__in=sadc_countries).order_by("name")

    medicine_prices = medicine_grid(procurements)

    writer.writerow(["SADC Prices"])
    headers = ["Medicine"] + list(countries)
    writer.writerow(headers)
    for medicine in medicine_prices:
        med_in_countries = medicine_prices[medicine]
        writer.writerow([medicine] + [fmt_price(med_in_countries[c]) for c in countries])

    proclist = procurement_list(procurements)

    writer.writerow([""])
    writer.writerow(["Recent Procurements"])
    writer.writerow([
        "Medicine", "Country", "Product", "Start Date", "End Date", "Volume (Packs)", "Pack Size", "Price per unit", "Supplier", "Incoterm"
    ])
    for medicine, procs in proclist.items():
        for p in procs:
            writer.writerow([
                medicine, p.country, p.product.name, 
                p.start_date, p.end_date, 
                p.volume, p.container.quantity, p.price_per_unit, 
                p.supplier, p.incoterm
            ])

    writer.writerow([""])
    writer.writerow(["Supplier Directory"])
    writer.writerow([
        "Medicine", "Name", "Country", "Address", "Website", "Contact", "Phone Number", "Alternative Phone Number", "Fax", "Email", "Alternative Email"
    ])

    _ = lambda x : ("%s" % x).encode("utf-8")
    for medicine, procs in proclist.items():
        for p in procs:
            supplier = p.supplier
            writer.writerow([
                _(medicine), _(supplier.name), _(supplier.country), _(supplier.address),
                _(supplier.website), _(supplier.contact), _(supplier.phone), 
                _(supplier.altphone), _(supplier.fax), _(supplier.email),
                _(supplier.altemail) 
            ])

    fp.close()
    return HttpResponse("Hello Word")
	
