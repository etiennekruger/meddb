import json
from datetime import datetime, date
from backend import db, logger
from backend import app
from operator import itemgetter

API_HOST = app.config["API_HOST"]


class CustomEncoder(json.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_obj = obj.strftime("%B %d, %Y, %H:%M")
        elif isinstance(obj, date):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            try:
                encoded_obj = json.dumps(obj.to_dict(), cls=CustomEncoder, indent=4)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = json.JSONEncoder.default(self, obj)
        return encoded_obj


def model_to_dict(obj):
    """
    Convert a single model object, or a list of model objects to dicts.
    Handle nested resources recursively.
    """

    # attributes from columns
    columns = obj.__mapper__.column_attrs.keys()
    tmp_dict = {
        key: getattr(obj, key) for key in columns
    }
    # attributes from relations are ignored
    return tmp_dict


def medicine_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    # resource URI
    tmp_dict['URI'] = API_HOST + 'medicine/' + str(obj.medicine_id) + '/'
    # name
    tmp_dict['name'] = obj.name
    # dosage form
    dosage_form = None
    if obj.dosage_form:
        dosage_form = obj.dosage_form.to_dict()
    tmp_dict['dosage_form'] = dosage_form
    tmp_dict.pop('dosage_form_id')
    # unit_of_measure
    unit_of_measure = None
    if obj.unit_of_measure:
        unit_of_measure = obj.unit_of_measure.value
    tmp_dict['unit_of_measure'] = unit_of_measure
    tmp_dict.pop('unit_of_measure_id')
    # benchmark prices
    benchmarks = []
    for benchmark in obj.benchmarks:
        benchmark_dict = benchmark.to_dict()
        benchmark_dict.pop('medicine_id')
        benchmarks.append(benchmark_dict)
    tmp_dict['benchmarks'] = benchmarks
    if include_related:
        # related products
        products = []
        for product in obj.products:
            product_dict = product.to_dict()
            product_dict.pop('medicine')
            products.append(product_dict)
        tmp_dict['products'] = sorted(products, key=itemgetter('average_price'))
        # related procurements
        procurements = []
        for procurement in obj.procurements:
            procurement_dict = procurement.to_dict()
            procurements.append(procurement_dict)
        tmp_dict['procurements'] = sorted(procurements, key=itemgetter('unit_price_usd'))
    return tmp_dict


def product_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    # resource URI
    tmp_dict['URI'] = API_HOST + 'product/' + str(obj.product_id) + '/'
    # average price, as calculated from procurement info
    if tmp_dict['average_price']:
        tmp_dict['average_price'] = float('%.3g' % tmp_dict['average_price'])
    # related manufacturer
    manufacturer = None
    if obj.manufacturer:
        manufacturer = obj.manufacturer.to_dict()
    tmp_dict['manufacturer'] = manufacturer
    tmp_dict.pop('manufacturer_id')
    tmp_dict['registrations'] = []
    for registration in obj.registrations:
        tmp_dict['registrations'].append(registration.to_dict())
    # medicine
    tmp_dict['medicine'] = obj.medicine.to_dict()
    tmp_dict.pop('medicine_id')
    if include_related:
        # related procurements
        procurements = []
        for procurement in obj.procurements:
            procurement_dict = procurement.to_dict(include_related=True)
            procurement_dict.pop('product_id')
            procurements.append(procurement_dict)
        tmp_dict['procurements'] = procurements
        # alternative products
        alternative_products = []
        for product in obj.alternative_products:
            product_dict = product.to_dict()
            alternative_products.append(product_dict)
        alternative_products = sorted(alternative_products, key=itemgetter('average_price'))
        tmp_dict['alternative_products'] = alternative_products
    return tmp_dict


def procurement_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    # resource URI
    tmp_dict['URI'] = API_HOST + 'procurement/' + str(obj.procurement_id) + '/'
    # product
    tmp_dict['product'] = obj.product.to_dict()
    # country
    tmp_dict['country'] = obj.country.to_dict() if obj.country else None
    tmp_dict.pop('country_id')
    # incoterm
    tmp_incoterm = None
    if obj.incoterm:
        tmp_incoterm = obj.incoterm.to_dict()
    tmp_dict['incoterm'] = tmp_incoterm
    tmp_dict.pop('incoterm_id')
    # source
    tmp_source = None
    if obj.source:
        tmp_source = obj.source.to_dict()
    tmp_dict['source'] = tmp_source
    tmp_dict.pop('source_id')
    # added & approved by
    tmp_added_by = None
    tmp_approved_by = None
    if obj.added_by:
        tmp_added_by = obj.added_by.to_dict()
    if obj.approved_by:
        tmp_approved_by = obj.approved_by.to_dict()
    tmp_dict['added_by'] = tmp_added_by
    tmp_dict['approved_by'] = tmp_approved_by
    tmp_dict.pop('added_by_id')
    tmp_dict.pop('approved_by_id')
    if include_related:
        # supplier
        tmp_supplier = None
        if obj.supplier:
            tmp_supplier = obj.supplier.to_dict()
        tmp_dict['supplier'] = tmp_supplier
        tmp_dict.pop('supplier_id')
        # currency
        tmp_currency = None
        if obj.currency:
            tmp_currency = obj.currency.to_dict()
            tmp_currency['rate'] = float('%.3g' % (tmp_dict['pack_price'] / tmp_dict['pack_price_usd']))
        tmp_dict['currency'] = tmp_currency
        tmp_dict.pop('currency_id')
    # round the price
    if tmp_dict['pack_price_usd']:
        tmp_dict['pack_price_usd'] = float('%.3g' % tmp_dict['pack_price_usd'])
    if tmp_dict['unit_price_usd']:
        tmp_dict['unit_price_usd'] = float('%.3g' % tmp_dict['unit_price_usd'])
    return tmp_dict


def manufacturer_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    # resource URI
    tmp_dict['URI'] = API_HOST + 'manufacturer/' + str(obj.manufacturer_id) + '/'
    # name
    tmp_dict['name'] = obj.get_name()
    # country
    tmp_country = None
    if obj.country:
        tmp_country = obj.country.to_dict()
    tmp_dict['country'] = tmp_country
    tmp_dict.pop('country_id')
    return tmp_dict


def supplier_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    # resource URI
    tmp_dict['URI'] = API_HOST + 'supplier/' + str(obj.supplier_id) + '/'
    if include_related:
        # products related to this supplier, as calculated from procurements
        products = []
        for product in obj.products:
            products.append(product.to_dict())
        tmp_dict['products'] = products
    return tmp_dict


def user_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    tmp_dict.pop('password_hash')
    # resource URI
    tmp_dict['URI'] = API_HOST + 'user/' + str(obj.user_id) + '/'
    return tmp_dict


def site_to_dict(obj, include_related=False):

    tmp_dict = model_to_dict(obj)
    # country
    tmp_country = None
    if obj.country:
        tmp_country = obj.country.to_dict()
    tmp_dict['country'] = tmp_country
    tmp_dict.pop('country_id')
    if include_related:
        # manufacturer
        tmp_dict['manufacturer'] = obj.manufacturer.to_dict()
        tmp_dict.pop('manufacturer_id')
    return tmp_dict


def queryset_to_json(obj_or_list, count=None, next=None, include_related=False):
    """
    Convert a single model object, or a list of model objects to dicts, before
    serializing the results as a json string.
    """

    if isinstance(obj_or_list, db.Model):
        # this a single object
        out = obj_or_list.to_dict(include_related=True)
    else:
        # this is a list of objects
        results = []
        for obj in obj_or_list:
            results.append(obj.to_dict(include_related=False))
        out = {
            'count': count,
            'next': next,
            'results': results
            }

    return json.dumps(out, cls=CustomEncoder, indent=4)