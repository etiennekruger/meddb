import requests
import json

API_ROOT = "http://medicines.sadc.int/meddb/json/"

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
        dump.append(rec)
    else:
        print "Error: " + str(r.status_code) + " " + tmp_url

f = open("dump.json", "w")
f.write(json.dumps(dump, indent=4))