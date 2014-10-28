from backend import db, models

products = models.Product.query.all()
product_names = []

for product in products:
    if product.name and not product.name in product_names:
        product_names.append(product.name)

product_names.sort()

for name in product_names:
    tmp = name.split(" ")[0]
    if tmp:
        tmp = tmp.title()
    else:
        tmp = ""
    print '"' + name + '": ' + '"' + tmp + '",'

manufacturers = models.Manufacturer.query.all()
manufacturer_names = []

for manufacturer in manufacturers:
    if manufacturer.name and not manufacturer.name in manufacturer_names:
        manufacturer_names.append(manufacturer.name)

manufacturer_names.sort()

for name in manufacturer_names:
    print '"' + name + '": ' + '"' + name + '",'
