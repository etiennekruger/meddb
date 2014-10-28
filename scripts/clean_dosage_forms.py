from backend.models import *
from backend import db


canonical_dosage_forms = [
    "capsule/tablet",
    "suspension",
    "injection",
    "inhaler",
    "cream",
    "ointment",
    "eye ointment",
    "eye drops",
    "ear drops",
    "pessary",
    "powder",
    "suppository",
    ]

dosage_form_map = {
    "Powder for suspension": "suspension",
    "ampoule": "injection",
    "cap/tab": "capsule/tablet",
    "eye drops": "",
    "eye ointment": "",
    "eye/ear drops": "eye drops",
    "infusion": "suspension",
    "inhaler": "",
    "injectable solution": "injection",
    "injection": "",
    "liquid": "suspension",
    "ointment": "",
    "pessary": "",
    "powder": "",
    "powder for injection": "injection",
    "powder for suspension": "suspension",
    "suspension": "",
    "syringe": "injection",
    "syrup": "suspension",
    "syrup/suspension": "suspension",
    "tablet": "capsule/tablet",
    "tablet (dispersible)": "capsule/tablet",
    "vial": "injection",
    }

# ensure all canonical dosage forms exist in db
for name in canonical_dosage_forms:
    dosage_form = DosageForm.query.filter_by(name=name).first()
    if dosage_form is None:
        dosage_form = DosageForm(name=name)
        db.session.add(dosage_form)
        db.session.commit()

# capture info in dosage form into product 'description' field
products = Product.query.all()
for product in products:
    if product.medicine.dosage_form:
        tmp = product.medicine.dosage_form.name
        if dosage_form_map.get(tmp):
            if not tmp in ["syrup/suspension", "cap/tab"]:
                if product.description:
                    tmp = product.description + " " + tmp
                product.description = tmp
                print tmp
                db.session.add(product)
db.session.commit()

# remove obsolete dosage forms, and reset foreign keys appropriately
for tmp in dosage_form_map.keys():
    if dosage_form_map.get(tmp):
        print "removing " + tmp
        old_dosage_form = DosageForm.query.filter_by(name=tmp).first()
        new_dosage_form = DosageForm.query.filter_by(name=dosage_form_map[tmp]).first()
        # switch medicine records to new target dosage form
        for medicine in old_dosage_form.medicines:
            # avoid duplicate medicines
            existing_medicine = Medicine.query.filter_by(name=medicine.name).filter_by(dosage_form=new_dosage_form).first()
            if existing_medicine is not None:
                # transfer Product foreign keys
                products = Product.query.filter_by(medicine=medicine).all()
                for product in products:
                    product.medicine = existing_medicine
                    db.session.add(product)
                db.session.commit()
                # transfer Benchmark foreign keys
                benchmarks = BenchmarkPrice.query.filter_by(medicine=medicine).all()
                for benchmark in benchmarks:
                    benchmark.medicine = existing_medicine
                    db.session.add(benchmark)
                db.session.commit()
                # delete Components
                components = Component.query.filter_by(medicine=medicine).all()
                for component in components:
                    db.session.delete(component)
                # delete Medicine
                db.session.delete(medicine)
                db.session.commit()
            else:
                medicine.dosage_form = new_dosage_form
                db.session.add(medicine)
                db.session.commit()
        # remove old dosage form record
        db.session.delete(old_dosage_form)
        db.session.commit()
