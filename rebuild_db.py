import backend.models as models
from backend import db
import json
from datetime import date, datetime

db.drop_all()
db.create_all()

# add first user
user_obj = models.User()
user_obj.email = 'adi@code4sa.org'
db.session.add(user_obj)
db.session.commit()

# populate items from 3rd party datasets:
# Country
with open("data/countries.json", "r") as f:
    countries = json.loads(f.read())
    for country in countries:
        country_obj = models.Country()
        country_obj.name = country["name"]
        country_obj.code = country["alpha-3"]
        country_obj.code_short = country["alpha-2"]
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
f = open("dump_medicines.json", "r")
medicines = json.loads(f.read())
f.close()

for medicine in medicines:

    medicine_obj = models.Medicine()

    # capture components
    for component in medicine["ingredients"]:
        ingredient_obj = models.Ingredient.query.filter(models.Ingredient.name==component["inn"]).first()
        if ingredient_obj is None:
            ingredient_obj = models.Ingredient()
            ingredient_obj.name = component["inn"]
            db.session.add(ingredient_obj)
            db.session.commit()

        component_obj = models.Component()
        component_obj.ingredient = ingredient_obj
        tmp_strength = component["strength"]
        if tmp_strength == "n/a":
            tmp_strength = None
        component_obj.strength = tmp_strength
        component_obj.medicine = medicine_obj
        db.session.add(component_obj)
        db.session.commit()

    # capture MSH benchmark price
    if medicine['mshprice']:
        benchmark_obj = models.BenchmarkPrice()
        benchmark_obj.name = "MSH"
        benchmark_obj.year = 2012
        benchmark_obj.price = medicine['mshprice']
        benchmark_obj.medicine = medicine_obj
        db.session.add(benchmark_obj)
        db.session.commit()
    else:
        tmp = "this medicine has no benchmark price: "
        if medicine.get('name'):
            tmp += medicine['name']
        else:
            tmp += str(medicine['id'])
        print tmp

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
        tmp = "this medicine has no dosage form: "
        if medicine.get('name'):
            tmp += medicine['name']
        else:
            tmp += str(medicine['id'])
        print tmp

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
        if tmp_code == "ANG":
            tmp_code = "AGO"
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
        tmp_manufacturer_name = procurement["manufacturer"]["name"]
        if tmp_manufacturer_name == "Unknown":
            tmp_manufacturer_name = None
        manufacturer_obj = models.Manufacturer.query \
            .filter(models.Manufacturer.name==tmp_manufacturer_name) \
            .filter(models.Manufacturer.country==tmp_country) \
            .first()
        if manufacturer_obj is None:
            if tmp_manufacturer_name or tmp_country:
                manufacturer_obj = models.Manufacturer()
                manufacturer_obj.name = tmp_manufacturer_name
                if tmp_country:
                    manufacturer_obj.country = tmp_country
                else:
                    print "Unknown country: " + tmp_country_name

        # capture site
        site_obj = None
        if procurement["product"].get('site'):
            site_obj = models.Site.query.filter(models.Site.name==procurement["product"]["site"]).first()
        if site_obj is None:
            site_obj = models.Site()
            if procurement["product"].get('site'):
                site_obj.name = procurement["product"]["site"]
            db.session.add(site_obj)
            db.session.commit()

        # capture product
        tmp_name = procurement["product"]["name"]
        if tmp_name == "":
            tmp_name = None
        product_obj = models.Product.query.filter(models.Product.name==tmp_name) \
            .filter(models.Product.medicine==medicine_obj) \
            .filter(models.Product.manufacturer==manufacturer_obj) \
            .first()
        if product_obj is None:
            product_obj = models.Product()
            product_obj.name = tmp_name
            product_obj.medicine = medicine_obj
            product_obj.manufacturer = manufacturer_obj
            if procurement["product"].get('generic'):
                product_obj.is_generic = bool(procurement["product"]["generic"])
            else:
                product_obj.is_generic = True
            db.session.add(product_obj)
            db.session.commit()

        # capture supplier
        supplier_obj = None
        if procurement.get("supplier"):
            tmp_name = procurement["supplier"]["name"]
            if tmp_name == "Unknown":
                tmp_name = None
            supplier_obj = models.Supplier.query.filter(models.Supplier.name==tmp_name).first()
            if not supplier_obj:
                supplier_obj = models.Supplier()
                supplier_obj.name = tmp_name
                db.session.add(supplier_obj)
                db.session.commit()

        # capture container
        container_obj = models.Container.query.filter(models.Container.type==procurement["container"]["type"]) \
            .filter(models.Container.quantity==procurement["container"]["quantity"]) \
            .filter(models.Container.unit==procurement["container"]["unit"]) \
            .first()
        if container_obj is None:
            container_obj = models.Container()
            container_obj.type = procurement["container"]["type"]
            container_obj.quantity = procurement["container"]["quantity"]
            container_obj.unit = procurement["container"]["unit"]
            db.session.add(container_obj)
            db.session.commit()

        # capture source
        source_obj = None
        if procurement.get("source") and procurement["source"]:
            tmp_name = procurement["source"]["name"].strip()
            if tmp_name == "":
                tmp_name = None
            tmp_url = procurement["source"]["url"].strip()
            if tmp_url == "":
                tmp_url = None
            tmp_date = procurement["source"]["date"].strip()
            if tmp_date:
                tmp_date = datetime.strptime(tmp_date, "%Y-%m-%d").date()
            source_obj = models.Source.query.filter(models.Source.name==tmp_name) \
                .filter(models.Source.date==tmp_date)\
                .filter(models.Source.url==tmp_url).first()
            if not source_obj:
                source_obj = models.Source()
                source_obj.name = tmp_name
                source_obj.date = tmp_date
                source_obj.url = tmp_url
                db.session.add(source_obj)
                db.session.commit()

        if procurement['incoterm']:
            incoterm_obj = models.Incoterm.query.filter(models.Incoterm.code==procurement['incoterm']['name']).first()
            procurement_obj.incoterm = incoterm_obj

        procurement_obj.added_by = user_obj
        procurement_obj.source = source_obj
        procurement_obj.container = container_obj
        procurement_obj.country = country_obj
        procurement_obj.supplier = supplier_obj
        procurement_obj.manufacturer = manufacturer_obj
        procurement_obj.product = product_obj
        procurement_obj.price = procurement["price"]
        procurement_obj.start_date = datetime.strptime(procurement["start_date"], "%Y-%m-%d")
        if procurement.get("end_date"):
            procurement_obj.end_date = datetime.strptime(procurement["end_date"], "%Y-%m-%d")
        procurement_obj.pack_size = procurement["packsize"]
        procurement_obj.volume = procurement["volume"]
        # note: we could call calculate_price_usd at this point, but let's rather work from existing data, since the API's rate limited
        procurement_obj.price_usd = procurement["price_usd"]

        db.session.add(procurement_obj)
        pass

    db.session.add(medicine_obj)

db.session.commit()

# calculate average product prices
products = models.Product.query.all()
for product in products:
    product.calculate_average_price()
    db.session.add(product)
db.session.commit()

# populate detailed supplier info
f = open("dump_suppliers.json", "r")
suppliers = json.loads(f.read())
f.close()

for supplier in suppliers:
    supplier_obj = None

    supplier_obj = models.Supplier.query.filter(models.Supplier.name==supplier['name']).first()
    if not supplier_obj:
        print "Unknown supplier: " + supplier['name']
        supplier_obj = models.Supplier()
        supplier_obj.name = supplier['name']

    if supplier["email"]:
        supplier_obj.email = supplier["email"]
    if supplier["altemail"]:
        supplier_obj.alt_email = supplier["altemail"]
    if supplier["address"]:
        supplier_obj.street_address = supplier["address"]
    if supplier["contact"]:
        supplier_obj.contact = supplier["contact"]
    if supplier["phone"]:
        supplier_obj.phone = supplier["phone"]
    if supplier["altphone"]:
        supplier_obj.alt_phone = supplier["altphone"]
    if supplier["fax"]:
        supplier_obj.fax = supplier["fax"]
    if supplier["website"]:
        supplier_obj.website = supplier["website"]

    db.session.add(supplier_obj)
db.session.commit()