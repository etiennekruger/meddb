import backend.models as models
from backend import db
import json
from datetime import date, datetime
import scrape_bechmarks
import maps


db.drop_all()
db.create_all()

# add first user & admin user
user_obj = models.User()
user_obj.email = 'adi@sarpam.net'
password = raw_input("Please enter a password:")
user_obj.password = password
user_obj.activated = True
user_obj.is_admin = True
db.session.add(user_obj)

admin_user_obj = models.User()
admin_user_obj.email = 'admin@sarpam.net'
admin_user_obj.password = password
admin_user_obj.activated = True
admin_user_obj.is_admin = True
db.session.add(admin_user_obj)

user2__obj = models.User()
user2__obj.email = 'petrus@code4sa.org'
user2__obj.password = password
user2__obj.activated = True
db.session.add(user2__obj)

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
procurements = {}
f = open("data/dump_procurements.json", "r")
tmp = json.loads(f.read())
f.close()
for tmp_proc in tmp:
    procurements[tmp_proc['id']] = tmp_proc

f = open("data/dump_medicines.json", "r")
medicines = json.loads(f.read())
f.close()

# dict for storing site info, which isn't included in the nested procurement record
product_sites = {}
for medicine in medicines:
    for product in medicine['products']:
        manufacturer =  product['manufacturer']
        if manufacturer.get('site') and not manufacturer['site'] in [None, "Uknown", "Unknown", "Unknown - Unknown"]:
            # capture site
            tmp_id = product['id']
            product_sites[tmp_id] = product['manufacturer']['site']

procurement_ids = []

dupe_records = [
    "Benzyl penicillin 5.0 mu vial ",
    "Ceftriaxone injection 500mg powder for injec",
    "Ciprofloxacin 250mg ",
    "Co-trimoxazole 480mg 400mg + 80mg ",
    "Efivarenz 600mg ",
    "Lamivudine 150mg ",
    "Lopinavir + ritonavir 80mg + 20mg ",
    "Metronidazole 400-500mg ",
    "Stavudine 30mg ",
]

for medicine in medicines:

    medicine_obj = models.Medicine()

    if not medicine["ingredients"]:
        if medicine['name'] == dupe_records[0]:
            medicine["ingredients"] = [
                {
                    "inn": "Benzyl penicillin",
                    "strength": "5mu",
                    "id": 10
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Benzyl penicillin (5mu)").first()
        elif medicine['name'] == dupe_records[1]:
            medicine["ingredients"] = [
                {
                    "inn": "Ceftriaxone injection",
                    "strength": "500mg",
                    "id": 13
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Ceftriaxone injection (500mg)").first()
        elif medicine['name'] == dupe_records[2]:
            medicine["ingredients"] = [
                {
                    "inn": "Ciprofloxacin",
                    "strength": "250mg",
                    "id": 17
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Ciprofloxacin (250mg)").first()
        elif medicine['name'] == dupe_records[3]:
            medicine["ingredients"] = [
                {
                    "inn": "Sulfamethoxazole",
                    "strength": "400mg",
                    "id": 79
                },
                {
                    "inn": "Trimethoprim",
                    "strength": "80mg",
                    "id": 78
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Sulfamethoxazole (400mg), Trimethoprim (80mg)").first()
        elif medicine['name'] == dupe_records[4]:
            medicine["ingredients"] = [
                {
                    "inn": "Efivarenz",
                    "strength": "600mg",
                    "id": 92
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Efivarenz (600mg)").first()
        elif medicine['name'] == dupe_records[5]:
            medicine["ingredients"] = [
                {
                    "inn": "Lamivudine",
                    "strength": "150mg",
                    "id": 77
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Lamivudine (150mg)").first()
        elif medicine['name'] == dupe_records[6]:
            medicine["ingredients"] = [
                {
                    "inn": "Lopinavir",
                    "strength": "80mg",
                    "id": 60
                },
                {
                    "inn": "Ritonavir",
                    "strength": "20mg",
                    "id": 81
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Lopinavir (80mg), Ritonavir (20mg)").first()
        elif medicine['name'] == dupe_records[7]:
            medicine["ingredients"] = [
                {
                    "inn": "Metronidazole",
                    "strength": "400-500mg",
                    "id": 29
                },
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Metronidazole (400-500mg)").first()
        elif medicine['name'] == dupe_records[8]:
            medicine["ingredients"] = [
                {
                    "inn": "Stavudine",
                    "strength": "30mg"
                }
            ]
            medicine_obj = models.Medicine.query.filter(models.Medicine.name=="Stavudine (30mg)").first()
            print "DISASTER AVERTED"
        else:
            print "SOOPER DOOPER ERROR"

    if medicine.get('name') not in dupe_records:
        # capture components
        for component in medicine["ingredients"]:
            ingredient_obj = models.Ingredient.query.filter(models.Ingredient.name==component["inn"]).first()
            if ingredient_obj is None:
                ingredient_obj = models.Ingredient()
                ingredient_obj.name = component["inn"]
                db.session.add(ingredient_obj)

            component_obj = models.Component()
            component_obj.ingredient = ingredient_obj
            tmp_strength = component["strength"].replace(" ", "")
            if tmp_strength:
                tmp_strength = tmp_strength.replace('miu', 'MIU').replace('iu', "IU")
            if tmp_strength == "n/a":
                tmp_strength = None
            component_obj.strength = tmp_strength
            component_obj.medicine = medicine_obj
            db.session.add(component_obj)

        # capture MSH benchmark price
        if medicine['mshprice']:
            benchmark_obj = models.BenchmarkPrice()
            benchmark_obj.name = "MSH"
            benchmark_obj.year = 2012
            benchmark_obj.price = medicine['mshprice']
            benchmark_obj.medicine = medicine_obj
            db.session.add(benchmark_obj)
        else:
            tmp = "this medicine has no benchmark price: "
            if medicine.get('name'):
                tmp += medicine['name']
            else:
                tmp += str(medicine['id'])
            print tmp

        # capture dosage form
        if medicine['dosageform'] and not medicine['dosageform'] == "N/A":
            dosage_form_name = maps.map_dosage_form(medicine['dosageform'])
            dosage_form_obj = models.DosageForm.query.filter(models.DosageForm.name==dosage_form_name).first()
            if dosage_form_obj is None:
                dosage_form_obj = models.DosageForm()
                dosage_form_obj.name = dosage_form_name
                db.session.add(dosage_form_obj)
            medicine_obj.dosage_form = dosage_form_obj
        else:
            tmp = "this medicine has no dosage form: "
            if medicine.get('name'):
                tmp += medicine['name']
            else:
                tmp += str(medicine['id'])
            print tmp

        medicine_obj.set_name()
        db.session.add(medicine_obj)
        try:
            db.session.commit()
        except Exception:
            print component_obj.ingredient.name
            raise

    # capture procurements
    for procurement in medicine["procurements"]:

        # save ID, so we can know which records to scrape from API.
        if not procurement['id'] in procurement_ids:
            procurement_ids.append(procurement['id'])

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
        if tmp_country_name in ["USA", "United States "]:
            tmp_country_name = "United States"
        if tmp_country_name == "DRC":
            tmp_country_name = "Congo (DRC)"
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
        if manufacturer_obj is None and tmp_manufacturer_name is not None:
            manufacturer_obj = models.Manufacturer()
            if tmp_manufacturer_name or tmp_country:
                manufacturer_obj.name = tmp_manufacturer_name
                manufacturer_obj.country = tmp_country
            db.session.add(manufacturer_obj)
            db.session.commit()

        # capture manufacturer site
        if manufacturer_obj is not None:
            tmp_site_name = None
            tmp_product_id = procurement["product"]["id"]
            if product_sites.get(tmp_product_id):
                tmp_site_name = product_sites[tmp_product_id]
            site_obj = models.Site.query \
                .filter(models.Site.manufacturer_id==manufacturer_obj.manufacturer_id) \
                .filter(models.Site.name==tmp_site_name) \
                .first()
            if site_obj is None and tmp_site_name is not None:
                site_obj = models.Site()
                site_obj.name = tmp_site_name
                site_obj.manufacturer = manufacturer_obj
                db.session.add(site_obj)
                db.session.commit()

        # capture product
        tmp_name = procurement["product"]["name"]
        if tmp_name == "":
            tmp_name = None
        product_obj = models.Product.query.filter(models.Product.name==maps.map_product_name(tmp_name)) \
            .filter(models.Product.medicine==medicine_obj) \
            .filter(models.Product.manufacturer==manufacturer_obj) \
            .filter(models.Product.site==site_obj) \
            .first()
        if product_obj is None:
            product_obj = models.Product()
            product_obj.name = maps.map_product_name(tmp_name)
            product_obj.medicine = medicine_obj
            product_obj.manufacturer = manufacturer_obj
            product_obj.site = site_obj
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
            if not supplier_obj and tmp_name is not None:
                supplier_obj = models.Supplier()
                supplier_obj.name = tmp_name
                db.session.add(supplier_obj)
                db.session.commit()


        # capture source
        source_obj = None
        tmp_proc = procurements.get(procurement["id"])
        if tmp_proc.get("source"):
            tmp_name = tmp_proc["source"]["name"].strip()
            if tmp_name == "":
                tmp_name = None
            tmp_url = tmp_proc["source"]["url"]
            if tmp_url:
                tmp_url = tmp_url.strip()
            if tmp_url == "":
                tmp_url = None
            tmp_date = tmp_proc["source"]["date"].strip()[0:10]
            if tmp_date:
                tmp_date = datetime.strptime(tmp_date, "%Y-%m-%d").date()
            source_obj = models.Source.query.filter(models.Source.name==tmp_name) \
                .filter(models.Source.date==tmp_date) \
                .filter(models.Source.url==tmp_url).first()
            if not source_obj:
                source_obj = models.Source()
                source_obj.name = tmp_name
                source_obj.date = tmp_date
                source_obj.url = tmp_url
                db.session.add(source_obj)
                db.session.commit()

        # capture currency relation
        if procurement['currency']:
            currency_obj = models.Currency.query.filter(models.Currency.code==procurement['currency']['code']).first()
            procurement_obj.currency = currency_obj

        # capture terms of transaction
        if procurement['incoterm']:
            incoterm_obj = models.Incoterm.query.filter(models.Incoterm.code==procurement['incoterm']['name']).first()
            procurement_obj.incoterm = incoterm_obj


        # capture container
        container = maps.map_container(procurement["container"]["type"].lower())
        procurement_obj.container = container
        pack_size = procurement["packsize"]
        try:
            pack_size = int(pack_size)
        except Exception:
            pack_size = 1
        if procurement["container"]["quantity"]:
            pack_size *= procurement["container"]["quantity"]
        procurement_obj.pack_size = pack_size
        procurement_obj.unit_of_measure = procurement["container"]["unit"]

        procurement_obj.added_by = user_obj
        procurement_obj.approved_by = admin_user_obj
        procurement_obj.source = source_obj
        procurement_obj.country = country_obj
        procurement_obj.supplier = supplier_obj
        procurement_obj.manufacturer = manufacturer_obj
        procurement_obj.product = product_obj

        procurement_obj.pack_price = procurement["price"]
        procurement_obj.pack_price_usd = procurement["price_usd"]
        procurement_obj.unit_price_usd = float(procurement["price_usd"])/pack_size

        procurement_obj.start_date = datetime.strptime(procurement["start_date"], "%Y-%m-%d")
        procurement_obj.added_on = datetime.strptime("2014-05-15", "%Y-%m-%d")
        procurement_obj.approved = True
        if procurement.get("end_date"):
            procurement_obj.end_date = datetime.strptime(procurement["end_date"], "%Y-%m-%d")

        procurement_obj.quantity = procurement["volume"]

        db.session.add(procurement_obj)
        pass

db.session.commit()

# calculate average product prices
products = models.Product.query.all()
for product in products:
    product.calculate_average_price()
    db.session.add(product)
db.session.commit()

# populate detailed supplier info
f = open("data/dump_suppliers.json", "r")
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

scrape_bechmarks.save_benchmark_records()

procurement_ids.sort()
print procurement_ids