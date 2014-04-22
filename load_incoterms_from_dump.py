import json

f = open("med-db/instance/incoterms.json", "r")
incoterms = json.loads(f.read())

d = open("dump.json", "r")
medicines = json.loads(d.read())

for medicine in medicines:
    for procurement in medicine["procurements"]:
        if not incoterms.get(procurement["incoterm"]["name"]):
            incoterms[procurement["incoterm"]["name"]] = procurement["incoterm"]["description"]
            print procurement["incoterm"]["name"] + ": " + procurement["incoterm"]["description"]

f.close()
d.close()