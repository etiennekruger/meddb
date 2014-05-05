import backend.models as models
from backend import db
import json

db.drop_all()
db.create_all()

f = open("dump.json", "r")
medicines = json.loads(f.read())
f.close()

print dir(medicines[0])

for medicine in medicines:
    
    medicine_obj = models.Medicine()

    # capture ingredients
    for ingredient in medicine["ingredients"]:
        component_obj = models.Component.query.filter(models.Component.name==ingredient["inn"]).first()
        if component_obj is None:
            component_obj = models.Component()
            component_obj.name = ingredient["inn"]
            db.session.add(component_obj)

        ingredient_obj = models.Ingredient()
        ingredient_obj.component = component_obj
        ingredient_obj.strength = ingredient["strength"]
        ingredient_obj.medicine = medicine_obj
        db.session.add(ingredient_obj)

    # capture MSH benchmark price
    if medicine['mshprice']:
        benchmark_obj = models.BenchmarkPrice()
        benchmark_obj.name = "msh"
        benchmark_obj.year = 2013
        benchmark_obj.price = medicine['mshprice']
        db.session.add(benchmark_obj)
    else:
        print "this medicine has no benchmark price: " + medicine['name']

    # capture dosage form
    if medicine['dosageform']:
        dosage_form_obj = models.DosageForm.query.filter(models.DosageForm.name==medicine['dosageform']).first()
        if dosage_form_obj is None:
            dosage_form_obj = models.DosageForm()
            dosage_form_obj.name = medicine['dosageform']
            db.session.add(dosage_form_obj)
        medicine_obj.dosage_form = dosage_form_obj
    else:
        print "Unknown dosage form"
        raise Exception

    db.session.add(medicine_obj)

    # capture procurements
    for procurement in medicine["procurements"]:
        # capture country

        # capture product

        # capture manufacturer

        # capture site

        # capture supplier

        pass



db.session.commit()
