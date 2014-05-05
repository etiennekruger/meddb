import backend.models as models
from backend import db
import json
from datetime import datetime

db.drop_all()
db.create_all()

# populate items from 3rd party datasets:
# Country
with open("data/countries.json", "r") as f:
    countries = json.loads(f.read())
    for country in countries:
        country_obj = models.Country()
        country_obj.name = country["name"]
        country_obj.code = country["alpha-3"]
        db.session.add(country_obj)
# Currency
with open("data/currencies.json", "r") as f:
    currencies = json.loads(f.read())
    for code, name in currencies.iteritems():
        currency_obj = models.Currency()
        currency_obj.name = name
        currency_obj.code = code
        db.session.add(currency_obj)
# Incoterm
with open("data/incoterms.json", "r") as f:
    incoterms = json.loads(f.read())
    for code, description in incoterms.iteritems():
        incoterm_obj = models.Incoterm()
        incoterm_obj.description = description
        incoterm_obj.code = code
        db.session.add(incoterm_obj)
db.session.commit()

# migrate data from json dump to new db
f = open("dump.json", "r")
medicines = json.loads(f.read())
f.close()

for medicine in medicines:
    
    medicine_obj = models.Medicine()

    # capture ingredients
    for ingredient in medicine["ingredients"]:
        component_obj = models.Component.query.filter(models.Component.name==ingredient["inn"]).first()
        if component_obj is None:
            component_obj = models.Component()
            component_obj.name = ingredient["inn"]
            db.session.add(component_obj)
            db.session.commit()

        ingredient_obj = models.Ingredient()
        ingredient_obj.component = component_obj
        ingredient_obj.strength = ingredient["strength"]
        ingredient_obj.medicine = medicine_obj
        db.session.add(ingredient_obj)
        db.session.commit()

    # capture MSH benchmark price
    if medicine['mshprice']:
        benchmark_obj = models.BenchmarkPrice()
        benchmark_obj.name = "msh"
        benchmark_obj.year = 2013
        benchmark_obj.price = medicine['mshprice']
        db.session.add(benchmark_obj)
        db.session.commit()
    else:
        print "this medicine has no benchmark price: " + medicine['name']

    # capture dosage form
    if medicine['dosageform'] and not medicine['dosageform'] == "N/A":
        dosage_form_obj = models.DosageForm.query.filter(models.DosageForm.name==medicine['dosageform']).first()
        if dosage_form_obj is None:
            dosage_form_obj = models.DosageForm()
            dosage_form_obj.name = medicine['dosageform']
            db.session.add(dosage_form_obj)
            db.session.commit()
        medicine_obj.dosage_form = dosage_form_obj
    else:
        print "Unknown dosage form for: " + medicine["name"]

    db.session.add(medicine_obj)
    db.session.commit()

    # capture procurements
    for procurement in medicine["procurements"]:
        procurement_obj = models.Procurement()

        # set country relation
        tmp_code = procurement["country"]["code"]
        if tmp_code == "LES":
            tmp_code = "LSO"
        if tmp_code == "MAW":
            tmp_code = "MWI"
        if tmp_code == "SEY":
            tmp_code = "SYC"
        country_obj = models.Country.query.filter(models.Country.code==tmp_code).first()
        if country_obj is None:
            print "Country could not be found: " + procurement["country"]["code"]

        # capture manufacturer
        tmp_country_name = procurement["manufacturer"]["country"][0]
        if tmp_country_name == "USA":
            tmp_country_name = "United States"
        if tmp_country_name == "DRC":
            tmp_country_name = "Democratic Republic of the Congo"
        if tmp_country_name == "Keyna":
            tmp_country_name = "Kenya"
        tmp_country = models.Country.query.filter(models.Country.name==tmp_country_name).first()
        manufacturer_obj = models.Manufacturer.query\
            .filter(models.Manufacturer.name==procurement["manufacturer"]["name"])\
            .filter(models.Manufacturer.country==tmp_country)\
            .first()
        if manufacturer_obj is None:
            manufacturer_obj = models.Manufacturer()
            manufacturer_obj.name = procurement["manufacturer"]["name"]
            if tmp_country and tmp_country.name!="Unknown":
                manufacturer_obj.country = tmp_country
            else:
                print "Unknown country: " + tmp_country_name

        # TODO: capture site

        # capture product
        product_obj = models.Product.query.filter(models.Product.name==procurement["product"]["name"])\
            .filter(models.Product.medicine==medicine_obj)\
            .filter(models.Product.manufacturer==manufacturer_obj)\
            .first()
        if product_obj is None:
            product_obj = models.Product()
            product_obj.name = procurement["product"]["name"]
            product_obj.medicine = medicine_obj
            product_obj.manufacturer = manufacturer_obj
            product_obj.is_generic = bool(procurement["product"]["generic"])
            db.session.add(product_obj)
            db.session.commit()

        # TODO: capture supplier

        procurement_obj.country = country_obj
        procurement_obj.manufacturer = manufacturer_obj
        procurement_obj.product = product_obj
        procurement_obj.price = procurement["price"]
        procurement_obj.start_date = datetime.strptime(procurement["start_date"], "%Y-%m-%d")
        procurement_obj.end_date = datetime.strptime(procurement["end_date"], "%Y-%m-%d")
        # TODO: add incoterm
        procurement_obj.pack_size = procurement["packsize"]
        procurement_obj.volume = procurement["volume"]

        db.session.add(procurement_obj)
        pass
