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
    
    db.session.add(medicine_obj)

    # capture procurements
    for procurement in medicine["procurements"]:
        # capture country

        # capture product

        # capture manufacturer

        # capture site

        # capture supplier

        pass

    # capture MSH benchmark price

    # capture dosage form


db.session.commit()
