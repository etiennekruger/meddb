import backend.models as models
from backend import db

db.drop_all()
db.create_all()

tmp = models.Source()
tmp.name = "Test Source"
db.session.add(tmp)

tmp = models.Country()
tmp.code = "RSA"
tmp.name = "South Africa"
db.session.add(tmp)

db.session.commit()