import requests
import json

API_ROOT = "http://medicines.sadc.int/meddb/json/"

# collect existing medicine info (with nested procurements)
r = requests.get(API_ROOT + "medicine/")
medicines = r.json()
print str(len(medicines)) + " medicines found"

dump = []

for medicine in medicines:
    tmp_url = API_ROOT + "medicine/" + str(medicine["id"]) + "/"
    r = requests.get(tmp_url)
    if r.status_code == 200:
        rec = r.json()
        if rec.get('name'):
            print rec["name"]
        else:
            print "unnamed medicine: " + str(medicine["id"])
        dump.append(rec)
    else:
        print "Error: " + str(r.status_code) + " " + tmp_url

with open("data/dump_medicines.json", "w") as f:
    f.write(json.dumps(dump, indent=4))

# collect existing supplier info
r = requests.get(API_ROOT + "supplier/")
suppliers = r.json()
print "\n" + str(len(suppliers)) + " suppliers found"

dump = []

for supplier in suppliers:
    tmp_url = API_ROOT + "supplier/" + str(supplier["id"]) + "/"
    r = requests.get(tmp_url)
    if r.status_code == 200:
        rec = r.json()
        if rec.get('name'):
            print rec["name"]
        else:
            print "unnamed supplier: " + str(supplier["id"])
        dump.append(rec)
    else:
        print "Error: " + str(r.status_code) + " " + tmp_url

with open("data/dump_suppliers.json", "w") as f:
    f.write(json.dumps(dump, indent=4))