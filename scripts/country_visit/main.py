import utils

headings = [
    "Product",
    "Pack size",
    "Quoted Pack Price",
    "Unit of Measure",
    "Multiplier",
    "Unit Price",
    "Incoterm",
    "Supplier",
    "Manufacturer",
    "Qty",
    "Total Spend (USD)",
    "Comparison Price",
    "Notes",
    "Potential Savings",
    ]

def dump_row(list_in):

    str_out = ""
    for item in list_in:
        str_out += str(item) + ", "
    str_out = str_out[0:-2]
    return str_out


def extract_csv_tanzania():
    headings_tanzania = [
        "Bidder No.",
        "Supplier",
        "Item Number",
        "Product",
        "Pack Size",
        "Curr.",
        "Pack Price",
        "Msd Price(TSH)",
        "Quantity",
        "Total Amount",
        "UOM",
        "Multiplier",
        ]

    reader = utils.get_reader('tanzania_tender.csv')
    recs = utils.map_data(headings_tanzania, reader)

    # sort list by total
    recs = utils.sort_list(recs, 'Total Amount')
    recs.reverse()

    str_out = ", ".join(headings) + "\n"
    for rec in recs:
        product = '"' + rec["Product"] + '"'
        print product
        pack_size = rec["Pack Size"]
        pack_price = rec["Pack Price"]
        term = "DDP"
        supplier = rec["Supplier"]
        manufacturer = "see tender doc"
        qty = rec["Quantity"]
        total = str(rec['Total Amount']).split(".")[0]
        uom = rec["UOM"]
        multiplier = rec["Multiplier"]
        unit_price = float(pack_price) / int(multiplier)
        str_out += dump_row([product, pack_size, pack_price, uom, multiplier, unit_price, term, supplier, manufacturer, qty, total, "", "", ""]) + "\n"

    with open('comparison_tanzania.csv', 'w') as f:
        f.write(str_out)
    return


def extract_csv_zambia():
    headings_zambia = [
        "PRODUCT No.",
        "Product",
        "Unit Pack Size",
        "Unit Price",
        "qty",
        "Manufacturer",
        "UOM",
        "Multiplier",
        ]

    reader = utils.get_reader('zambia_framework_contract.csv')
    recs = utils.map_data(headings_zambia, reader)

    # clean price
    for rec in recs:
        try:
            rec["Unit Price"] = float(rec["Unit Price"].replace("$", ""))
        except Exception as e:
            print rec["Product"] + ": " + rec["Unit Price"]
            raise e

    # add a field for the total amount
    for rec in recs:
        try:
            rec["total amount"] = rec["Unit Price"] * rec["qty"]
        except Exception as e:
            print rec["Product"]
            print rec["Unit Price"]
            print rec["qty"]
            print type(rec["Unit Price"])
            print type(rec["qty"])
            raise e

    # sort list by total
    recs = utils.sort_list(recs, "total amount")
    recs.reverse()

    str_out = ", ".join(headings) + "\n"

    for rec in recs:

        product = '"' + rec["Product"] + '"'
        print product
        pack_size = rec["Unit Pack Size"]
        pack_price = rec["Unit Price"]
        qty = rec["qty"]
        total = str(rec['total amount']).split(".")[0]
        uom = rec["UOM"]
        multiplier = rec["Multiplier"]
        unit_price = float(pack_price) / int(multiplier)
        term = "CIP"
        supplier = "UNIMED"
        manufacturer = rec["Manufacturer"]

        str_out += dump_row([product, pack_size, pack_price, uom, multiplier, unit_price, term, supplier, manufacturer, qty, total, "", "", ""]) + "\n"

    with open('comparison_zambia.csv', 'w') as f:
        f.write(str_out)

if __name__ == "__main__":

    extract_csv_tanzania()
    extract_csv_zambia()