from backend.models import *
from backend import db


canonical_units = [
    "each",
    "dose",
    "ml",
    "litre",
    "IU",
    "MIU",
    "g",
    "mg",
    "mcg",
    ]

unit_map = {
    None: "each",
    "IU": "",
    "L": "litre",
    "MIU": "",
    "MU": "MIU",
    "ampoule": "each",
    "cap/tab": "each",
    "capsule": "each",
    "dose": "",
    "film coated tablet": "each",
    "g": "",
    "item": "each",
    "litre": "",
    "mg": "",
    "ml": "",
    "pessaries (with applicators)": "each",
    "pessary": "each",
    "sachet": "each",
    "syringe": "each",
    "tablet": "each",
    "tablet (film coated)": "each",
    "tablet (scored)": "each",
    "unit": "each",
    "vial": "each",
    }

# clean unit field in Procurement model
procurements = Procurement.query.all()
for procurement in procurements:
    key = None
    if procurement.unit_of_measure:
        key = procurement.unit_of_measure
    if unit_map[key]:
        procurement.unit_of_measure = unit_map[key]
    db.session.add(procurement)
db.session.commit()

# create all the canonical units
for unit in canonical_units:
    unit_of_measure = UnitOfMeasure(value=unit)
    db.session.add(unit_of_measure)
db.session.commit()

# relate medicines to appropriate uom's from their procurements
for procurement in Procurement.query.all():
    medicine = procurement.product.medicine
    if not medicine.unit_of_measure_id:
        uom = UnitOfMeasure.query.filter_by(value=procurement.unit_of_measure).first()
        medicine.unit_of_measure = uom
        db.session.add(medicine)
db.session.commit()