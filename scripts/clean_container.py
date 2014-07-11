from backend.models import *
from backend import db

canonical_containers = [
    "container",
    "bottle",
    "blister/strip",
    "ampoule",
    "vial",
    "syringe",
    "bag",
    "tube",
    "sachet",
    ]

container_map = {
    None: "container",
    "ampoule": "",
    "bottle": "",
    "bottle - powder for mixture": "bottle",
    "box": "container",
    "boxed blister pack": "blister/strip",
    "inhaler": "",
    "injection": "container",
    "injection - syringe": "container",
    "item": "container",
    "pack": "container",
    "pack/tin": "container",
    "patient ready pack": "container",
    "powder for 1ml injection": "container",
    "syringe": "",
    "tin": "container",
    "tube": "",
    "vial": "",
    }

# clean Procurement container field
procurements = Procurement.query.all()
for procurement in procurements:
    if container_map[procurement.container]:
        print container_map[procurement.container]
        procurement.container = container_map[procurement.container]
        db.session.add(procurement)
    else:
        print procurement.container
db.session.commit()

# add container options for admin form
for option in canonical_containers:
    available_container = AvailableContainers(value=option)
    db.session.add(available_container)
db.session.commit()