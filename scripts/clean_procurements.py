from backend import db
from backend.models import *

country = Country.query.get(248)  # Zambia
medicine = Medicine.query.get(4)  # Artemether (20mg), Lumefantrine (120mg)
products = Product.query.filter(Product.medicine==medicine).all()

for product in products:
    print "woohoo"
    procurements = Procurement.query.filter_by(product=product).all()
    for procurement in procurements:
        if procurement.unit_price_usd < 0.01:
            print "\tstuff"
            print procurement.country.name
            procurement.approved = False
            db.session.add(procurement)
db.session.commit()
