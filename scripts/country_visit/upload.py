import utils
from main import headings
from backend.models import *
import json
from datetime import datetime


def upload_csv(filename, source_name, source_date, country_code, date_from, date_to):

    reader = utils.get_reader(filename)
    recs = utils.map_data(headings, reader)

    user = User.query.filter(User.email=='petrus@code4sa.org').first()
    admin_user = User.query.filter(user.email=='admin@sarpam.net').first()
    USD = Currency.query.filter(Currency.code=='USD').first()
    procurement_country = Country.query.filter(Country.code==country_code).first()

    for rec in recs:

        print json.dumps(rec, indent=4)

        tmp = rec['Product'].split("+")
        for i in range(len(tmp)):
            tmp[i] = tmp[i].strip()
            tmp[i] = tmp[i] if tmp[i] else None

        fields = [
            "medicine",
            "dosage_form",
            "strength",
            "volume",
            "notes",
            ]

        extra_fields = {}
        for i in range(len(tmp)):
            extra_fields[fields[i]] = tmp[i]

        countries = {
            "UK": Country.query.filter(Country.name=="United Kingdom").first(),
            "India": Country.query.filter(Country.name=="India").first(),
            "China": Country.query.filter(Country.name=="China").first(),
            }

        # manufacturer
        manufacturer_obj = None
        if rec["Manufacturer"] and not "see tender doc" in rec["Manufacturer"]:
            tmp_name, tmp_country_name = rec["Manufacturer"].split("/")
            # print tmp_name, tmp_country_name
            manufacturer_obj = Manufacturer.query.filter(Manufacturer.name==tmp_name).first()
            if not manufacturer_obj:
                manufacturer_obj = Manufacturer()
                manufacturer_obj.name = tmp_name
                manufacturer_obj.country = countries[tmp_country_name]
                manufacturer_obj.added_by = user
                db.session.add(manufacturer_obj)
                db.session.commit()

        # supplier
        supplier_obj = None
        if rec["Supplier"]:
            supplier_obj = Supplier.query.filter(Supplier.name==rec["Supplier"]).first()
            if not supplier_obj:
                supplier_obj = Supplier()
                supplier_obj.name = rec["Supplier"]
                supplier_obj.added_by = user
                db.session.add(supplier_obj)
                db.session.commit()

        # dosage form
        if extra_fields["dosage_form"]:
            tmp_dosage_form = extra_fields["dosage_form"].lower()
            if tmp_dosage_form in ['capsule', 'tablet']:
                tmp_dosage_form = "cap/tab"
            dosage_form_obj = DosageForm.query.filter(DosageForm.name==tmp_dosage_form).first()
            if extra_fields["dosage_form"] and not dosage_form_obj:
                dosage_form_obj = DosageForm()
                dosage_form_obj.name = extra_fields["dosage_form"]
        else:
            dosage_form_obj = None

        # ingredient
        ingredient_obj = Ingredient.query.filter(Ingredient.name==extra_fields["medicine"]).first()
        if not ingredient_obj:
            ingredient_obj = Ingredient()
            ingredient_obj.name = extra_fields["medicine"]
            db.session.add(ingredient_obj)
            db.session.commit()

        # component
        tmp_strength = None
        if extra_fields.get('strength'):
            tmp_strength = extra_fields['strength'].lower().replace("and", "+").replace(" ", "")
        component_obj = Component.query.filter(Component.ingredient==ingredient_obj) \
            .filter(Component.strength==tmp_strength).first()
        if component_obj and component_obj.medicine.dosage_form == dosage_form_obj:
            medicine_obj = component_obj.medicine
        else:
            medicine_obj = Medicine()
            medicine_obj.dosage_form = dosage_form_obj
            db.session.add(medicine_obj)

            component_obj = Component()
            component_obj.ingredient = ingredient_obj
            component_obj.strength = tmp_strength
            component_obj.medicine = medicine_obj
            db.session.add(component_obj)
            medicine_obj.set_name()
            db.session.commit()

        # product
        product_obj = Product.query.filter(Product.medicine==medicine_obj) \
            .filter(Product.manufacturer==manufacturer_obj).first()
        if not product_obj:
            product_obj = Product()
            product_obj.medicine = medicine_obj
            product_obj.manufacturer = manufacturer_obj
            product_obj.added_by = user
            db.session.add(product_obj)
            db.session.commit()

        # container
        tmp_container_type = None
        if rec["Unit of Measure"] in ['ampoule', 'syringe', 'item', 'vial',]:
            tmp_container_type = rec["Unit of Measure"]
        elif rec["Unit of Measure"] in ['cap/tab',]:
            tmp_container_type = "pack/tin"
        tmp_unit = rec["Unit of Measure"]
        tmp_pack_size = rec["Pack size"]

        # incoterm
        incoterm_obj = Incoterm.query.filter(Incoterm.code==rec["Incoterm"]).first()

        # source
        source_obj = Source.query.filter(Source.name==source_name).first()
        if not source_obj:
            source_obj = Source()
            source_obj.name = source_name
            source_obj.date = datetime.strptime(source_date, "%Y-%m-%d")
            db.session.add(source_obj)
            db.session.commit()

        # procurement
        procurement_obj = Procurement()
        procurement_obj.source = source_obj
        procurement_obj.product = product_obj
        product_obj.added_by = user
        procurement_obj.approved_by = admin_user
        procurement_obj.pack_price = rec["Quoted Pack Price"]
        procurement_obj.pack_price_usd = rec["Quoted Pack Price"]
        procurement_obj.pack_size = tmp_pack_size
        procurement_obj.unit_price_usd = float(procurement_obj.pack_price_usd)/tmp_pack_size
        procurement_obj.container = tmp_container_type
        procurement_obj.unit_of_measure = tmp_unit
        procurement_obj.quantity = rec["Qty"]
        procurement_obj.currency = USD
        procurement_obj.incoterm = incoterm_obj
        procurement_obj.country = procurement_country
        procurement_obj.added_on = datetime.strptime("2014-06-23", "%Y-%m-%d")
        procurement_obj.approved = True
        procurement_obj.start_date = date_from
        procurement_obj.end_date = date_to
        db.session.add(procurement_obj)
        db.session.commit()

        # update product's average price
        product_obj.calculate_average_price()
        db.session.add(product_obj)
        db.session.commit()

    return


if __name__ == "__main__":

    date_from = datetime.strptime("2012-08-01", "%Y-%m-%d")
    date_to = datetime.strptime("2014-08-31", "%Y-%m-%d")
    upload_csv('comparison_zambia.csv', 'Zambia - Framework contract extension, 2012 to 2014', "2014-06-12", 'ZMB', date_from, date_to)

    date_from = datetime.strptime("2013-01-01", "%Y-%m-%d")
    date_to = datetime.strptime("2014-12-31", "%Y-%m-%d")
    upload_csv('comparison_tanzania.csv', 'Tanzania - TENDER 30 ILS 59 ITEMS 15.07.2013', "2014-06-09", 'TZA', date_from, date_to)