import backend.models as models
from backend import db
import json
from datetime import date, datetime
import scrape_bechmarks


def map_product_name(product_name):

    product_names = {
        " EFAVIRENZ 50mg capsule": "Efavirenz",
        "2 ABACAVIR 300mg tablet, 56 (60) tablets  ": "Abacavir",
        "ABACAVIR 60mg dispersible  tablets  (56) 60 tablets": "Abacavir",
        "ABACAVIR 300mg tablet, 56 (60) tablets": "Abacavir",
        "ACICLOVIR 200mg dispersible tablet, 25  tablets": "Aciclovir",
        "AMYN 250": "Amyn",
        "AMYN 500": "Amyn",
        "AMYN S 125": "Amyn",
        "Acriptaz": "Acriptaz",
        "Adco - Lamivudine and Zidovudine 150/300": "Adco-Lamivudine/Zidovudine",
        "Adco Omeprazole 20mg": "Adco Omeprazole",
        "Adco-Diclophenac 25": "Adco-Diclophenac",
        "Adco-Diclophenac 50": "Adco-Diclophenac",
        "Adco-Lamivudine": "Adco-Lamivudine",
        "Adco-Metronidazole": "Adco-Metronidazole",
        "Adco-Metronidazole 400": "Adco-Metronidazole",
        "Adco-Nevirapine": "Adco-Nevirapine",
        "Adco-Abacavir 300mg  tablets": "Adco-Abacavir",
        "Albusol 20%": "Albusol",
        "Allergex": "Allergex",
        "Aluvia": "Aluvia",
        "Aluvia 200/50mg": "Aluvia",
        "Amirol-Amitriptyline 25mg": "Amirol-Amitriptyline",
        "Amitryptiline Tabs": "Amitryptiline",
        "Amoxen-Amoxycilin 25mg/ml": "Amoxen-Amoxycilin",
        "Amoxicap-Amoxycillin 250mg Capsules": "Amoxicap-Amoxycillin",
        "Amoxicillin": "Amoxicillin",
        "Amoxicillin 125mg/5ml suspension": "Amoxicillin",
        "Amoxicillin 250mg cap/tab": "Amoxicillin",
        "Amoxicillin 500mg cap/tab": "Amoxicillin",
        "Anaerobyl 400": "Anaerobyl",
        "Artementer Lumefantrine": "Artementer Lumefantrine",
        "Aspen Lamivudine 150mg": "Aspen-Lamivudine",
        "Aspen Nevirapine 200mg": "Aspen-Nevirapine",
        "Aspen Stavudine": "Aspen-Stavudine",
        "Asthavent MDI 200": "Asthavent MDI 200",
        "Asthavent MDI 300": "Asthavent MDI 300",
        "Asthavent MDI 300 + Zerostat Spacer": "Asthavent MDI 300 + Zerostat Spacer",
        "Austell - Metformin 500mg": "Austell-Metformin",
        "Austell - Simvastatin 10mg": "Austell-Simvastatin",
        "Austell Simvastatin 20mg": "Austell-Simvastatin",
        "BENZATHINE PENICILLIN G 2,4 mega units  powder for injection, vi": "Benzathine Penicillin G 2,4 mega units",
        "BENZYLPENICILLIN SODIUM 1 mega unit  powder for injection, vial.": "Benzylpenicillin Sodium 1 mega unit",
        "BENZYLPENICILLIN SODIUM 5 mega unit  powder for injection, vial": "Benzylpenicillin Sodium 5 mega unit",
        "Barrs Paracetamol Syrup": "Barrs Paracetamol Syrup",
        "Bendex": "Bendex",
        "Benkil 400": "Benkil",
        "Benzyl penicillin 5.0 mu vial 5mu vial": "Benzyl penicillin",
        "Betamycin 250": "Betamycin",
        "Betapam": "Betapam",
        "Bio-Metronidazole 400": "Bio-Metronidazole",
        "Biotech Ciprofloxacin": "Biotech-Ciprofloxacin",
        "Bleolem": "Bleolem",
        "CEFTRIAXONE 500 mg powder for injection,  via": "Ceftriaxone",
        "CEFTRIAXONE 500 mg powder for injection,  vial": "Ceftriaxone",
        "CHLORPHENIRAMINE MALEATE, TAB 4MG": "Chlorpheniramine Maleate",
        "CIPROFLOXACIN 250mg Tablet": "Ciprofloxacin",
        "CIPROFLOXACIN 500mg tablet": "Ciprofloxacin",
        "CIPROFLOXACIN, TAB 250MG": "Ciprofloxacin,",
        "Captopril 25mg cap/tab": "Captopril",
        "Carbamazepine 200mg cap/tab": "Carbamazepine",
        "Ceftriaxone 250mg pdr for injection": "Ceftriaxone",
        "Ceftriaxone 250mg powder for injec": "Ceftriaxone",
        "Ceftriaxone injection 1g vial": "Ceftriaxone",
        "Chlorpheniramine 4mg cap/tab": "Chlorpheniramine",
        "Cipla - Lamivudine 150": "Cipla-Lamivudine",
        "Ciploxx": "Ciploxx",
        "Ciprofloxacin 250mg cap/tab": "Ciprofloxacin",
        "Ciprofloxacin 500mg cap/tab": "Ciprofloxacin",
        "Clotrimazole 100mg pessary": "Clotrimazole",
        "Co-trimoxazole 240mg/5ml 200mg/5ml + 40mg/5ml syrup/susp": "Co-Trimoxazole",
        "Co-trimoxazole 480mg 400mg + 80mg ": "Co-Trimoxazole",
        "Co-trimoxazole 480mg 400mg + 80mg cap/tab": "Co-Trimoxazole",
        "Coartem": "Coartem",
        "Colamziv": "Colamziv",
        "Combivir": "Combivir",
        "Degranol 200mg": "Degranol",
        "Depo Provera": "Depo Provera",
        "Diazepam 5mg cap/tab": "Diazepam",
        "Diclofenac 25 Biotech": "Biotech-Diclofenac",
        "Diclofenac 25mg cap/tab": "Diclofenac",
        "Diclofenac 50mg cap/tab": "Diclofenac",
        "Diclomax": "Diclomax",
        "Divuwin": "Divuwin",
        "Duovir": "Duovir",
        "Efivarenz 200mg tablets": "Efivarenz",
        "Efivarenz 50mg tablets": "Efivarenz",
        "Efivarenz 600mg tablets": "Efivarenz",
        "Epsitron": "Epsitron",
        "Ermycin": "Ermycin",
        "Eryko 250": "Eryko",
        "Erythromycin 250mg cap/tab": "Erythromycin",
        "Erythromycin Stearate 250mg": "Erythromycin Stearate",
        "Glaxo-Ferrous salts": "Glaxo-Ferrous salts",
        "Glibenclamide 5mg cap/tab": "Glibenclamide",
        "Glibex5": "Glibex5",
        "Gulf Amitriptyline": "Gulf-Amitriptyline",
        "Gynatam": "Gynatam",
        "HUMAN COAGULATION CONCENTRATE COMPLEX: FACTOR VIII  COMPLEX 500 ": "Human coagulation concentrate complex: Factor viii, Complex 500",
        "Haemosolvate Factor VIII 300 IU": "Haemosolvate Factor VIII 300 IU",
        "Herpex-Acyclovir 200mg": "Herpex-Acyclovir",
        "Ilvitrim Suspension": "Ilvitrim",
        "Ilvitrim tablets  ": "Ilvitrim",
        "Indo Amoxycillin 250": "Indo-Amoxycillin",
        "Indo Amoxycillin 500": "Indo-Amoxycillin",
        "Indo Metformin 500": "Indo-Metformin",
        "Insulin isophane 100 iu/ml injection": "Insulin Isophane",
        "Insuman Basal 10ml": "Insuman Basal",
        "Karna": "Karna",
        "Kocef 250mg": "Kocef",
        "Lamivudine + Nevirapine + Stavudine 60mg + 12mg + 100mg cap/tab": "Lamivudine/Nevirapine/Stavudine",
        "Lamivudine + Nevirapine + Zidovudine 150 + 200 + 300 tablets": "Lamivudine/Nevirapine/Zidovudine",
        "Lamivudine + Zidovudine 150mg + 300mg cap/tab": "Lamivudine/Zidovudine",
        "Lamivudine 150mg cap/tab": "Lamivudine",
        "Levonorgestrel 0.75mg N/A": "Levonorgestrel",
        "Lopinavir + Ritonavir 100mg + 25mg tablets": "Lopinavir/Ritonavir",
        "Lopinavir + Ritonavir 200mg + 50mg tablets": "Lopinavir/Ritonavir",
        "Lopinavir + Ritonavir 80mg + 20mg syrup/susp": "Lopinavir/Ritonavir",
        "Lovire": "Lovire",
        "MEDROXYPROGESTERONE ACETATE, PWD FOR IM INJ, 150MG": "Medroxyprogesterone Acetate",
        "MOXYMAX 250": "Moxymax",
        "MOXYMAX 500": "Moxymax",
        "MOXYMAX S 125": "Moxymax",
        "Magnesium sulphate 500mg/ml injection": "Magnesium sulphate",
        "Martin Magnesium Sulphate 500mg/ml inj. 2ml": "Martin Magnesium Sulphate",
        "Measles vaccine n/a injection": "Measles vaccine",
        "Metformin 500mg cap/tab": "Metformin",
        "Metronidazole 200mg cap/tab": "Metronidazole",
        "Metronidazole 400-500mg cap/tab": "Metronidazole",
        "Mylan Captopril 25": "Mylan Captopril",
        "Mylan Metformin 500mg": "Mylan Metformin",
        "Nevirapine 200mg cap/tab": "Nevirapine",
        "Nevirapine 50mg/2ml syrup/susp": "Nevirapine",
        "Nevirapine 50mg/5ml syrup/susp": "Nevirapine",
        "Nivaquine 200mg": "Nivaquine",
        "Norlevo": "Norlevo",
        "Nucotrim": "Nucotrim",
        "OXYTOCIN IV INJ, 10IU/ML 1ML AMP": "Oxytocin",
        "Oframax 250": "Oframax",
        "Omeprazole 20mg cap/tab": "Omeprazole",
        "Omez 10": "Omez",
        "Oral rehydration salts who formula powder": "Oral rehydration salts (WHO formula)",
        "Oxytocin 10iu/ml injection": "Oxytocin",
        "Paracetamol 120mg/5ml suspension": "Paracetamol",
        "Petogen Fresenius": "Petogen Fresenius",
        "Protaphane (HM) GE Flexpen": "Protaphane (HM) GE Flexpen",
        "Ranceph 250": "Ranceph",
        "Remedica": "Remedica",
        "Remedium": "Remedium",
        "Resmed Cotrimoxazole Oral Suspension": "Resmed Cotrimoxazole",
        "Rhesugam IM": "Rhesugam IM",
        "Rifanah FC 200/150": "Rifanah FC 200/150",
        "Sabax-Magnesium Sulphate": "Sabax-Magnesium Sulphate",
        "Sandoz Amitriptyline HCl": "Sandoz Amitriptyline HCl",
        "Simvotin 10mg": "Simvotin",
        "Simvotin 20mg": "Simvotin",
        "Sonke Lamivudine 150mg": "Sonke Lamivudine",
        "Stavudine 30mg cap/tab": "Stavudine",
        "Storilat": "Storilat",
        "Tamoplex 20mg": "Tamoplex",
        "Tegretol 200mg": "Tegretol",
        "Tegretol 400mg": "Tegretol",
        "Tenofovir + Efivarenz + Lamivudine 300mg + 600mg + 300mg tablets": "Tenofovir/Efivarenz/Lamivudine",
        "Tenofovir + Lamivudine 300mg + 300 mg tablets": "Tenofovir/Lamivudine",
        "Tetracycline 0.01 eye oint": "Tetracycline",
        "Trepiline 10mg": "Trepiline",
        "Trepiline 25mg": "Trepiline",
        "Triotemp": "Triotemp",
        "Tumocin-15": "Tumocin-15",
        "Vitaforce Ferovite 200mg": "Vitaforce Ferovite",
        "Wormadole": "Wormadole",
        "ZIDOVUDINE 300mg tablet": "Zidovudine",
        "Zidovudine 300 tablets": "Zidovudine",
        "amoxicillin 500mg capsule": "Amoxicillin",
        }
    if product_names.get(product_name):
        product_name = product_names[product_name]
    return product_name


def map_manufacturer_names(name):

    manufacturer_names = {
        "Abbott GmbH & Co": "Abbott Laboratories",
        "Abbott Laboratories": "Abbott Laboratories",
        "Adcock Ingram Criticalcare Pty Ltd": "Adcock Ingram Criticalcare Pty Ltd",
        "Adcock Ingram Healthcare Pty Ltd": "Adcock Ingram",
        "Adcock Ingram Ltd": "Adcock Ingram",
        "Agio Pharmaceutical factor ": "Agio Pharmaceutical factor ",
        "Ajanta": "Ajanta",
        "Alembic Limited": "Alembic Limited",
        "Alfa Intes": "Alfa Intes",
        "Alkem Laboratories LTD": "Alkem Laboratories LTD",
        "Amstelfarma": "Amstelfarma",
        "Apotex": "Apotex",
        "Aspen": "Aspen Pharmacare",
        "Aspen Pharmacare": "Aspen Pharmacare",
        "Astrazeneca Pharmaceuticals Pty Ltd": "Astrazeneca Pharmaceuticals Pty Ltd",
        "Aurobindo": "Aurobindo",
        "BDH": "BDH",
        "Barrs Pharmaceutical Industries (Pty) Ltd": "Barrs Pharmaceutical Industries (Pty) Ltd",
        "Basi": "Basi",
        "Be-Tabs Pharmaceuticals": "Be-Tabs Pharmaceuticals",
        "Bio Nova Pharma": "Bio Nova Pharma",
        "Bio-Pen": "Bio-Pen",
        "Biotech Laboratories (Pty) Ltd": "Biotech Laboratories (Pty) Ltd",
        "Bodene Pty Ltd": "Bodene Pty Ltd",
        "Bristol-Myers Squibb": "Bristol-Myers Squibb",
        "CSPC Zhongnuo Pharmaceutical (Shijiazhuang) Co. Ltd": "CSPC Zhongnuo Pharmaceutical (Shijiazhuang) Co. Ltd",
        "Catalent France Osny S.A.S": "Catalent France Osny S.A.S",
        "Cipla Limited": "Cipla Limited",
        "Cipla Medpro (Pty) Ltd": "Cipla Medpro (Pty) Ltd",
        "Cipla Okasa Pharma Satara": "Cipla Okasa Pharma Satara",
        "Dawa Limited": "Dawa Limited",
        "Dr Reddy": "Dr Reddy",
        "Elys Chemicals Industries Ltd": "Elys Chemicals Industries Ltd",
        "F. Hoffmann- La Roche": "F. Hoffmann- La Roche",
        "FDC Ltd": "FDC Ltd",
        "Farmacuba": "Farmacuba",
        "Forts": "Forts",
        "Fourrts (India) Lab. PVT. Ltd": "Fourrts (India) Lab. PVT. Ltd",
        "Fresenius Kabi": "Fresenius Kabi",
        "GSK": "GSK",
        "Galentic Pharma (India) Pvt. Ltd": "Galentic Pharma (India) Pvt. Ltd",
        "Gedeon Richter": "Gedeon Richter",
        "Genepharm S.A.": "Genepharm S.A.",
        "Genpharm Inc": "Genpharm Inc",
        "Gland Pharma Limited": "Gland Pharma Limited",
        "Glaxo Smithkline South Africa Pty Ltd": "Glaxo Smithkline South Africa Pty Ltd",
        "Glenmark Pharmaceuticals": "Glenmark Pharmaceuticals",
        "Gracure Pharmaceutical Ltd": "Gracure Pharmaceutical Ltd",
        "Health Care Pharma PVT LTD": "Health Care Pharma PVT LTD",
        "Hetero Drugs Limited": "Hetero Drugs Limited",
        "I.J. Pharmaceutical": "I.J. Pharmaceutical",
        "IPCA Laboratories": "IPCA Laboratories",
        "Indico": "Indico",
        "Indoco Remedies": "Indoco Remedies",
        "KBI": "KBI",
        "Karnakata Antibiotics and Pharmaceuticals Limited": "Karnakata Antibiotics and Pharmaceuticals Limited",
        "Kedrion": "Kedrion",
        "Keko Pharmaceutical Industries Ltd": "Keko Pharmaceutical Industries Ltd",
        "Kent": "Kent",
        "Khandelwal Laboratories PVT LTD": "Khandelwal Laboratories PVT LTD",
        "Kocef": "Kocef",
        "Kopran Ltd": "Kopran Ltd",
        "Laborate": "Laborate",
        "Laboratorios Liconsa S.A.": "Laboratorios Liconsa S.A.",
        "Lemery SA.": "Lemery SA.",
        "Lincoln Pharmaceuticals Ltd": "Lincoln Pharmaceuticals Ltd",
        "Lupin Limited": "Lupin Limited",
        "MCPC": "MCPC",
        "Macleods Pharmaceuticals Limited": "Macleods Pharmaceuticals Limited",
        "Martindale Pharmaceuticals": "Martindale Pharmaceuticals",
        "Mascareignes": "Mascareignes",
        "Medicamen Biotech": "Medicamen Biotech",
        "Medico Remedies": "Medico Remedies",
        "Medix Care (Pty) Ltd": "Medix Care (Pty) Ltd",
        "Medochemie Ltd": "Medochemie Ltd",
        "Medopharma Ltd": "Medopharma Ltd",
        "Micro Labs": "Micro Labs",
        "Milan": "Milan",
        "Milpharm": "Milpharm",
        "Mylan Laboratories Limited": "Mylan Laboratories Limited",
        "NCPC International Corporation": "NCPC International Corporation",
        "NV Pharma manufacturing": "NV Pharma manufacturing",
        "Natal Bioproducts Institute": "Natal Bioproducts Institute",
        "New Cesamex Labo SPRL": "New Cesamex Labo SPRL",
        "Ningbo Tisun Medic Biochemic Co. Ltd": "Ningbo Tisun Medic Biochemic Co. Ltd",
        "Nirma": "Nirma",
        "Nova Argentia Industria Farmaceutica": "Nova Argentia Industria Farmaceutica",
        "Novartis - US": "Novartis - US",
        "Novartis Farma S.P.A": "Novartis Farma S.P.A",
        "Novartis South Africa (Pty) Ltd": "Novartis South Africa (Pty) Ltd",
        "PSI": "PSI",
        "Penilente LA ": "Penilente LA",
        "Pfeizer Laboratories Pty Ltd": "Pfeizer Laboratories Pty Ltd",
        "Pharma-Q (Pty) Ltd": "Pharma-Q (Pty) Ltd",
        "Pharmanova": "Pharmanova",
        "Phatkin Labo SPRL": "Phatkin Labo SPRL",
        "Plus Five": "Plus Five",
        "Premier Pharma Trade Pty Ltd": "Premier Pharma Trade Pty Ltd",
        "Radicura": "Radicura",
        "Ranbaxy": "Ranbaxy",
        "Ratnamani": "Ratnamani",
        "Remedica Ltd": "Remedica Ltd",
        "Rhydburg Pharmaceuticals": "Rhydburg Pharmaceuticals",
        "Rociject": "Rociject",
        "S. Kant Healthcare Ltd": "S. Kant Healthcare Ltd",
        "SADM  Pharmaceutical Ltd": "SADM Pharmaceutical Ltd",
        "Sandoz": "Sandoz",
        "Sandoz Pty LTD": "Sandoz Pty LTD",
        "Sanofi Aventis": "Sanofi-Aventis",
        "Sanofi Pasteur": "Sanofi Pasteur",
        "Sanofi Synthe Lab": "Sanofi Synthe Lab",
        "Sanofi-Aventis Deutschland GmbH": "Sanofi-Aventis",
        "Sanofi-Aventis Pty Ltd": "Sanofi-Aventis",
        "Serum Institute": "Serum Institute",
        "Sinochem Nongbo Ltd": "Sinochem Nongbo Ltd",
        "Stallion Laboratories": "Stallion Laboratories",
        "Sterop": "Sterop",
        "Teva": "Teva",
        "Tonghua Dongbao Pharmaceutical Co. Ltd": "Tonghua Dongbao Pharmaceutical Co. Ltd",
        "Torrent Pharmaceuticals Ltd": "Torrent Pharmaceuticals Ltd",
        "Umedica Laboratories PVT. LTD": "Umedica Laboratories PVT. LTD",
        "Unique Pharmaceutical Laboratories": "Unique Pharmaceutical Laboratories",
        "Universal Corporation": "Universal Corporation",
        "Varichem Pharmaceuticals Pty Ltd": "Varichem Pharmaceuticals Pty Ltd",
        "Waterland": "Waterland",
        "West Coast Pharmaceutical Works ": "West Coast Pharmaceutical Works",
        "Winthrop Pharmaceuticals (Pty) Ltd": "Winthrop Pharmaceuticals (Pty) Ltd",
        "Wockhardt Ltd": "Wockhardt Ltd",
        "Xixia  Pharmaceuticals": "Xixia Pharmaceuticals",
        "Zenufa Labo SPRL": "Zenufa Labo SPRL",
        "Zimplex": "Zinplex",
        "Zinplex": "Zinplex",
        }

    if manufacturer_names.get(name):
        name = manufacturer_names[name]
    return name

def map_dosage_form(dosage_form):

    dosage_forms = {
        'cap/tab': 'cap/tab',
        'vial': 'vial',
        'powder': 'powder',
        'eye oint': 'eye ointment',
        'injection': 'injection',
        'powder for injec': 'powder for injection',
        'syrup/susp': 'syrup/susp',
        'pessary': 'pessary',
        'dispersible tab': 'dispersible tab',
        'tablets': 'cap/tab',
        'suspension': 'syrup/susp',
        'syrup': 'syrup/susp',
        'susp': 'syrup/susp',
        'infusion': 'infusion',
        }
    if dosage_forms.get(dosage_form):
        return dosage_forms[dosage_form]
    return dosage_form


db.drop_all()
db.create_all()

# add first user & admin user
user_obj = models.User()
user_obj.email = 'adi@sarpam.net'
password = raw_input("Please enter a password:")
user_obj.password = password
user_obj.activated = True
user_obj.is_admin = True
db.session.add(user_obj)

admin_user_obj = models.User()
admin_user_obj.email = 'admin@sarpam.net'
admin_user_obj.password = password
admin_user_obj.activated = True
admin_user_obj.is_admin = True
db.session.add(admin_user_obj)

db.session.commit()

# populate items from 3rd party datasets:
# Country
with open("data/countries.json", "r") as f:
    countries = json.loads(f.read())
    for country in countries:
        country_obj = models.Country()
        country_obj.name = country["name"]
        country_obj.code = country["alpha-3"]
        country_obj.code_short = country["alpha-2"]
        db.session.add(country_obj)
# Currency
with open("data/currencies.json", "r") as f:
    currencies = json.loads(f.read())
    for code, name in currencies.iteritems():
        currency_obj = models.Currency()
        currency_obj.name = name
        currency_obj.code = code
        db.session.add(currency_obj)
# Incoterm
with open("data/incoterms.json", "r") as f:
    incoterms = json.loads(f.read())
    for code, description in incoterms.iteritems():
        incoterm_obj = models.Incoterm()
        incoterm_obj.description = description
        incoterm_obj.code = code
        db.session.add(incoterm_obj)
db.session.commit()

# migrate data from json dump to new db
f = open("data/dump_medicines.json", "r")
medicines = json.loads(f.read())
f.close()


for medicine in medicines:

    medicine_obj = models.Medicine()

    # capture components
    for component in medicine["ingredients"]:
        ingredient_obj = models.Ingredient.query.filter(models.Ingredient.name==component["inn"]).first()
        if ingredient_obj is None:
            ingredient_obj = models.Ingredient()
            ingredient_obj.name = component["inn"]
            db.session.add(ingredient_obj)
            db.session.commit()

        component_obj = models.Component()
        component_obj.ingredient = ingredient_obj
        tmp_strength = component["strength"]
        if tmp_strength == "n/a":
            tmp_strength = None
        component_obj.strength = tmp_strength
        component_obj.medicine = medicine_obj
        db.session.add(component_obj)
        db.session.commit()

    # capture MSH benchmark price
    if medicine['mshprice']:
        benchmark_obj = models.BenchmarkPrice()
        benchmark_obj.name = "MSH"
        benchmark_obj.year = 2012
        benchmark_obj.price = medicine['mshprice']
        benchmark_obj.medicine = medicine_obj
        db.session.add(benchmark_obj)
        db.session.commit()
    else:
        tmp = "this medicine has no benchmark price: "
        if medicine.get('name'):
            tmp += medicine['name']
        else:
            tmp += str(medicine['id'])
        print tmp

    # capture dosage form
    if medicine['dosageform'] and not medicine['dosageform'] == "N/A":
        dosage_form_name = map_dosage_form(medicine['dosageform'])
        dosage_form_obj = models.DosageForm.query.filter(models.DosageForm.name==dosage_form_name).first()
        if dosage_form_obj is None:
            dosage_form_obj = models.DosageForm()
            dosage_form_obj.name = dosage_form_name
            db.session.add(dosage_form_obj)
            db.session.commit()
        medicine_obj.dosage_form = dosage_form_obj
    else:
        tmp = "this medicine has no dosage form: "
        if medicine.get('name'):
            tmp += medicine['name']
        else:
            tmp += str(medicine['id'])
        print tmp

    db.session.add(medicine_obj)
    db.session.commit()

    # capture procurements
    for procurement in medicine["procurements"]:
        procurement_obj = models.Procurement()

        # set country relation
        tmp_code = procurement["country"]["code"]
        if tmp_code == "LES":
            tmp_code = "LSO"
        if tmp_code == "MAW":
            tmp_code = "MWI"
        if tmp_code == "SEY":
            tmp_code = "SYC"
        if tmp_code == "ANG":
            tmp_code = "AGO"
        country_obj = models.Country.query.filter(models.Country.code==tmp_code).first()
        if country_obj is None:
            print "Country could not be found: " + procurement["country"]["code"]

        # capture manufacturer
        tmp_country_name = procurement["manufacturer"]["country"][0]
        if tmp_country_name in ["USA", "United States "]:
            tmp_country_name = "United States"
        if tmp_country_name == "DRC":
            tmp_country_name = "Congo (DRC)"
        if tmp_country_name == "Keyna":
            tmp_country_name = "Kenya"
        tmp_country = models.Country.query.filter(models.Country.name==tmp_country_name).first()
        tmp_manufacturer_name = procurement["manufacturer"]["name"]
        if tmp_manufacturer_name == "Unknown":
            tmp_manufacturer_name = None
        manufacturer_obj = models.Manufacturer.query \
            .filter(models.Manufacturer.name==tmp_manufacturer_name) \
            .filter(models.Manufacturer.country==tmp_country) \
            .first()
        if manufacturer_obj is None:
            if tmp_manufacturer_name or tmp_country:
                manufacturer_obj = models.Manufacturer()
                manufacturer_obj.name = tmp_manufacturer_name
                if tmp_country:
                    manufacturer_obj.country = tmp_country
                else:
                    print "Unknown country: " + tmp_country_name

        # capture site
        site_obj = None
        if procurement["product"].get('site'):
            site_obj = models.Site.query.filter(models.Site.name==procurement["product"]["site"]).first()
        if site_obj is None:
            site_obj = models.Site()
            if procurement["product"].get('site'):
                site_obj.name = procurement["product"]["site"]
            db.session.add(site_obj)
            db.session.commit()

        # capture product
        tmp_name = procurement["product"]["name"]
        if tmp_name == "":
            tmp_name = None
        product_obj = models.Product.query.filter(models.Product.name==tmp_name) \
            .filter(models.Product.medicine==medicine_obj) \
            .filter(models.Product.manufacturer==manufacturer_obj) \
            .first()
        if product_obj is None:
            product_obj = models.Product()
            product_obj.name = map_product_name(tmp_name)
            product_obj.medicine = medicine_obj
            product_obj.manufacturer = manufacturer_obj
            if procurement["product"].get('generic'):
                product_obj.is_generic = bool(procurement["product"]["generic"])
            else:
                product_obj.is_generic = True
            db.session.add(product_obj)
            db.session.commit()

        # capture supplier
        supplier_obj = None
        if procurement.get("supplier"):
            tmp_name = procurement["supplier"]["name"]
            if tmp_name == "Unknown":
                tmp_name = None
            supplier_obj = models.Supplier.query.filter(models.Supplier.name==tmp_name).first()
            if not supplier_obj:
                supplier_obj = models.Supplier()
                supplier_obj.name = tmp_name
                db.session.add(supplier_obj)
                db.session.commit()

        # capture container
        procurement["container"]["type"] = procurement["container"]["type"].lower()
        if procurement["container"]["type"] == "ampoules":
            procurement["container"]["type"] = "ampoule"
        container_obj = models.Container.query.filter(models.Container.type==procurement["container"]["type"]) \
            .filter(models.Container.quantity==procurement["container"]["quantity"]) \
            .filter(models.Container.unit==procurement["container"]["unit"]) \
            .first()
        if container_obj is None:
            container_obj = models.Container()
            container_obj.type = procurement["container"]["type"]
            container_obj.quantity = procurement["container"]["quantity"]
            container_obj.unit = procurement["container"]["unit"]
            db.session.add(container_obj)
            db.session.commit()

        # capture source
        source_obj = None
        if procurement.get("source") and procurement["source"]:
            tmp_name = procurement["source"]["name"].strip()
            if tmp_name == "":
                tmp_name = None
            tmp_url = procurement["source"]["url"].strip()
            if tmp_url == "":
                tmp_url = None
            tmp_date = procurement["source"]["date"].strip()
            if tmp_date:
                tmp_date = datetime.strptime(tmp_date, "%Y-%m-%d").date()
            source_obj = models.Source.query.filter(models.Source.name==tmp_name) \
                .filter(models.Source.date==tmp_date) \
                .filter(models.Source.url==tmp_url).first()
            if not source_obj:
                source_obj = models.Source()
                source_obj.name = tmp_name
                source_obj.date = tmp_date
                source_obj.url = tmp_url
                db.session.add(source_obj)
                db.session.commit()

        # capture currency relation
        if procurement['currency']:
            currency_obj = models.Currency.query.filter(models.Currency.code==procurement['currency']['code']).first()
            procurement_obj.currency = currency_obj

        # capture terms of transaction
        if procurement['incoterm']:
            incoterm_obj = models.Incoterm.query.filter(models.Incoterm.code==procurement['incoterm']['name']).first()
            procurement_obj.incoterm = incoterm_obj

        procurement_obj.added_by = user_obj
        procurement_obj.approved_by = admin_user_obj
        procurement_obj.source = source_obj
        procurement_obj.container = container_obj
        procurement_obj.country = country_obj
        procurement_obj.supplier = supplier_obj
        procurement_obj.manufacturer = manufacturer_obj
        procurement_obj.product = product_obj
        procurement_obj.price = procurement["price"]
        procurement_obj.start_date = datetime.strptime(procurement["start_date"], "%Y-%m-%d")
        procurement_obj.added_on = datetime.strptime("2014-05-15", "%Y-%m-%d")
        procurement_obj.approved_on = datetime.strptime("2014-05-17", "%Y-%m-%d")
        if procurement.get("end_date"):
            procurement_obj.end_date = datetime.strptime(procurement["end_date"], "%Y-%m-%d")
        procurement_obj.pack_size = procurement["packsize"]
        procurement_obj.volume = procurement["volume"]
        # note: we could call calculate_price_usd at this point, but let's rather work from existing data, since the API's rate limited
        procurement_obj.price_usd = procurement["price_usd"]

        db.session.add(procurement_obj)
        pass

    db.session.add(medicine_obj)

db.session.commit()

# calculate average product prices
products = models.Product.query.all()
for product in products:
    product.calculate_average_price()
    db.session.add(product)
db.session.commit()

# populate detailed supplier info
f = open("data/dump_suppliers.json", "r")
suppliers = json.loads(f.read())
f.close()

for supplier in suppliers:
    supplier_obj = None

    supplier_obj = models.Supplier.query.filter(models.Supplier.name==supplier['name']).first()
    if not supplier_obj:
        print "Unknown supplier: " + supplier['name']
        supplier_obj = models.Supplier()
        supplier_obj.name = supplier['name']

    if supplier["email"]:
        supplier_obj.email = supplier["email"]
    if supplier["altemail"]:
        supplier_obj.alt_email = supplier["altemail"]
    if supplier["address"]:
        supplier_obj.street_address = supplier["address"]
    if supplier["contact"]:
        supplier_obj.contact = supplier["contact"]
    if supplier["phone"]:
        supplier_obj.phone = supplier["phone"]
    if supplier["altphone"]:
        supplier_obj.alt_phone = supplier["altphone"]
    if supplier["fax"]:
        supplier_obj.fax = supplier["fax"]
    if supplier["website"]:
        supplier_obj.website = supplier["website"]

    db.session.add(supplier_obj)
db.session.commit()

scrape_bechmarks.save_benchmark_records()