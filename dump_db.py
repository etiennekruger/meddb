import requests
import json

API_ROOT = "http://localhost:8000/json/"

r = requests.get(API_ROOT + "medicine/")

medicines = r.json()

print str(len(medicines)) + " medicines found"

dump = []

for medicine in medicines:
    r = requests.get(API_ROOT + "medicine/" + str(medicine["id"]) + "/")
    rec = r.json()
    print rec["name"]
    dump.append(rec)

f = open("dump.json", "w")
f.write(json.dumps(dump, indent=4))