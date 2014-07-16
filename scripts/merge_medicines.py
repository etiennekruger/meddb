from backend import db
from backend.models import *

medicines_for_removal = [
    177,
    147,
    162,
    160,
    ]

for medicine_id in medicines_for_removal:
    medicine = Medicine.query.get(medicine_id)
    print "Removing: " + medicine.name
    # remove procurements
    products = Product.query.filter(Product.medicine==medicine).all()
    for product in products:

        procurements = Procurement.query.filter(Procurement.product==product).all()
        for procurement in procurements:
            db.session.delete(procurement)
            print "deleting procurement " + str(procurement.procurement_id)
        # remove product
        db.session.delete(product)

    # remove benchmarks
    benchmarks = BenchmarkPrice.query.filter(BenchmarkPrice.medicine==medicine).all()
    for benchmark in benchmarks:
        db.session.delete(benchmark)
        print "deleting benchmark " + str(benchmark.benchmark_price_id)

    # remove medicine
    db.session.delete(medicine)
    db.session.commit()



def transfer_medicine(target_id, redundant_id):

    target_medicine = Medicine.query.get(target_id)
    redundant_medicine = Medicine.query.get(redundant_id)
    print "Transferring Medicine: " + str(redundant_medicine.name)

    # delete benchmarks
    benchmarks = BenchmarkPrice.query.filter(BenchmarkPrice.medicine==redundant_medicine).all()
    if benchmarks:
        for benchmark in benchmarks:
            print "Deleting benchmark"
            db.session.delete(benchmark)

    # transfer products to target medicine
    products = Product.query.filter(Product.medicine==redundant_medicine).all()
    for product in products:
        # check for duplicate products
        duplicates = Product.query.filter(Product.medicine==target_medicine) \
            .filter(Product.description==product.description) \
            .filter(Product.manufacturer_id==product.manufacturer_id) \
            .filter(Product.site_id==product.site_id).all()
        if duplicates:
            print "duplicates found: " + str(len(duplicates))
            for duplicate_product in duplicates:
                # transfer procurements to target product
                procurements = Procurement.query.filter(Procurement.product==duplicate_product).all()
                for procurement in procurements:
                    procurement.product = product
                    db.session.add(procurement)
                # delete redundant product
                db.session.delete(duplicate_product)
        print "Transferring product " + str(product.product_id)
        product.medicine = target_medicine
        db.session.add(product)

    # remove old medicine
    db.session.delete(medicine)
    db.session.commit()


# list of (target, [redundant]) medicine id's
medicines_for_merging = [
    (129, [197, 5]),
    (6, 184),
    (98, 55),
    (159, 35),
    (112, [176, 27]),
    (90, 181),
    (155, 199),
    (102, 200),
    (18, 185),
    (165, 111),
    (74, 80),
    (101, 20),
    (174, 93),
    (144, 179),
    (110, 194),
    (21, 132),
    (191, [167, 139]),
    ]

for target_id, removals in medicines_for_merging:
    medicine = Medicine.query.get(target_id)
    print "\nTarget: " + medicine.name

    try:
        for redundant_id in removals:
            medicine = Medicine.query.get(redundant_id)
            transfer_medicine(target_id, redundant_id)
    except TypeError:
        redundant_id = removals
        medicine = Medicine.query.get(redundant_id)
        transfer_medicine(target_id, redundant_id)
