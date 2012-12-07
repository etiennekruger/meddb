import urllib2
try:
    import simplejson as json
except ImportError:
    import json

from django.conf import settings
from django.views.generic.simple import direct_to_template

BASE_URL = getattr(settings, 'MEDDB_DATA_URL', '')

def _grab(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    if response.getcode() != 200:
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
    return direct_to_template(request, 'medicine_list.html', extra_context={ 'data': data })

def medicine(request, _id):
    url = '%s/json/medicine/%d/' % (BASE_URL, int(_id))
    data = _grab(url)
    formulation = ' + '.join([i['inn'] for i in data['ingredients']])
    data['formulation'] = formulation
    strength = ' + '.join([i['strength'] for i in data['ingredients']])
    data['strength'] = strength
    return direct_to_template(request, 'medicine.html', extra_context={ 'data': data })
