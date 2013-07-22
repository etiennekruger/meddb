import urllib2
import logging
try:
    import simplejson as json
except ImportError:
    import json

from django.conf import settings
from django.views.generic.simple import direct_to_template

logger = logging.getLogger(__name__)

BASE_URL = getattr(settings, 'MEDDB_DATA_URL', '')

def _grab(url):
    logger.info("Grabbing data: %s" % url)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    if response.getcode() != 200:
        logger.error("Error data: %s" % response.getcode())
        return None
    object = json.load(response)
    return object

def medicine_list(request):
    url = '%s/json/medicine/' % BASE_URL
    data = _grab(url)
    for medicine in data:
        formulation = ' + '.join([i['inn'] for i in medicine['ingredients']])
        medicine['formulation'] = formulation
        strength = ' + '.join([i['strength'] for i in medicine['ingredients']])
        medicine['strength'] = strength
    data.sort(key=lambda x: x['formulation'])
    return direct_to_template(request, 'medicine_list.html', extra_context={ 'data': data })

def medicine(request, _id):
    url = '%s/json/medicine/%d/' % (BASE_URL, int(_id))
    data = _grab(url)
    formulation = ' + '.join([i['inn'] for i in data['ingredients']])
    data['formulation'] = formulation
    strength = ' + '.join([i['strength'] for i in data['ingredients']])
    data['strength'] = strength
    sort_key = {
        'country': lambda x: x['country']['name'],
        'price_per_unit': lambda x: x['price_per_unit'],
        'incoterm': lambda x: x['incoterm'],
        'pack_size': lambda x: x['container']['quantity'],
        'volume': lambda x: x['volume'],
        'start_date': lambda x: x['start_date'],
        }[request.GET.get('sort', 'country')]
    data['procurements'].sort(key=sort_key)
    if request.GET.get('reverse', 'false') == 'true':
        data['procurements'].reverse()
    extra_context = {
        'data': data,
        'sort': request.GET.get('sort', 'country'),
        'reverse': request.GET.get('reverse', 'false') == 'true'
        }
    return direct_to_template(request, 'medicine.html', extra_context=extra_context)
