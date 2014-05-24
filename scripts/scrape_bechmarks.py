from bs4 import BeautifulSoup
import backend.models as models
from backend import db
from sqlalchemy.exc import IntegrityError

with open("data/The Global Fund Business Intelligence and Reporting Environment.html", 'r') as f:

    global_fund_doc = f.read()

soup = BeautifulSoup(global_fund_doc)

table = soup.find(id="saw_12246_3")
rows = table.find_all('tr')

cols = [0, 1, 2, 3, 6]
titles = ['formulation', 'strength', 'unit', 'CHAI_ceiling', 'PQR_median']

records = []
for i, row in enumerate(rows[2::]):
    cells = row.find_all('td')
    rec = {}
    for j, col in enumerate(cols):
        tmp = None
        try:
            tmp = str(cells[cols[j]].text.decode('utf-8'))
        except UnicodeEncodeError:
            pass
        rec[titles[j]] = tmp
    if rec['CHAI_ceiling'] or rec['PQR_median']:
        records.append(rec)
    print str(i) + " " + str(rec)


def extract_ingredients(formulation):
    tmp = formulation.split("(")[0]
    tmp = tmp.split("-")[0]
    tmp = tmp.split("+")
    names = []
    for name in tmp:
        names.append(name.strip())
    return names


def extract_strengths(strength):

    tmp = strength.split("/")
    postfix = ""
    if len(tmp) > 1:
        postfix = "/" + tmp[-1]
    tmp = tmp[0].split("+")
    strengths = []
    for strength in tmp:
        strengths.append(strength.strip() + postfix)
    return strengths

medicines = []
tmp = db.session.query(models.Medicine).all()
for item in tmp:
    medicine = item.to_dict()
    if medicine.get('components'):
        tmp_ingredients = []
        tmp_strengths = []
        for component in medicine['components']:
            tmp_ingredients.append(component['ingredient']['name'])
            tmp_strengths.append(component['strength'])
        tmp_ingredients.sort()
        tmp_strengths.sort()
        medicine['tmp_ingredients'] = tmp_ingredients
        medicine['tmp_strengths'] = tmp_strengths
        medicines.append(medicine)

for rec in records:
    rec['ingredients'] = extract_ingredients(rec['formulation'])
    rec['ingredients'].sort()
    rec['strengths'] = extract_strengths(rec['strength'])
    rec['strengths'].sort()
    for medicine in medicines:
        if medicine['tmp_ingredients'] == rec['ingredients']:
            # the ingredients match, now check the strengths
            if medicine['tmp_strengths'] == rec['strengths']:
                # strengths match, so let's log the benchmark price for this medicine
                medicine_obj = db.session.query(models.Medicine).get(medicine['medicine_id'])
                if rec['CHAI_ceiling']:
                    benchmark_obj = models.BenchmarkPrice()
                    benchmark_obj.name = "Clinton Health Access Initiative (CHAI)"
                    benchmark_obj.year = 2011
                    benchmark_obj.price = float(rec['CHAI_ceiling'])
                    benchmark_obj.medicine = medicine_obj
                    try:
                        db.session.add(benchmark_obj)
                        db.session.commit()
                        print "New CHAI benchmark: " + str(rec['ingredients']) + " " + str(rec['strengths'])
                    except IntegrityError:
                        db.session.remove()
                        print 'CHAI record already exists: ' + str(rec['ingredients']) + " " + str(rec['strengths'])
                        pass
                if rec['PQR_median']:
                    benchmark_obj = models.BenchmarkPrice()
                    benchmark_obj.name = "Global Fund, PQR median"
                    benchmark_obj.year = 2011
                    benchmark_obj.price = float(rec['PQR_median'])
                    benchmark_obj.medicine = medicine_obj
                    try:
                        db.session.add(benchmark_obj)
                        db.session.commit()
                        print "New PQR benchmark: " + str(rec['ingredients']) + " " + str(rec['strengths'])
                    except IntegrityError:
                        db.session.remove()
                        print 'PQR record already exists: ' + str(rec['ingredients']) + " " + str(rec['strengths'])
                        pass