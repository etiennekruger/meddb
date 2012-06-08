import django.utils.simplejson as json
from django import http
from django.views.generic import View

import models

# Setup memcache for nginx.
import memcache
mc=memcache.Client(['192.168.122.1:11211'])

# View base classes.
#
# These base classes simplify the implementation of the JSON represenation views
# for the individual models.

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload."
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object."
        return json.dumps(context, indent=2)


class JSONView(JSONResponseMixin, View):
    def get_json_data(self, *args, **kwargs):
        "Return a Python object that will be serialized into a JSON response."
        return {
            'params': kwargs
        }

    def get(self, request, *args, **kwargs):
        "Serialize the JSON data into an HTTP response."
        context = self.get_json_data(*args, **kwargs)
        response = self.render_to_response(context)
        key = request.path.encode('ascii','ignore')
        mc.set(key, response.content, 60*60*24*2)
        return response

class JSONRepresentation(JSONView):
    def get_json_data(self, *args, **kwargs):
        self.instance = self.model.objects.select_related().get(pk=kwargs['object_id'])
        return self.instance.as_dict()

class JSONList(JSONView):
    def get_json_data(self, *args, **kwargs):
        return [i.as_dict(minimal=True) for i in self.model.objects.select_related().all()]

# JSON Representation of the individual models.
#
# These classes render the acutal model details as a JSON object.

class CountryView(JSONRepresentation):
    model = models.Country

class CountryListView(JSONList):
    model = models.Country

class INNView(JSONRepresentation):
    model = models.INN

class INNListView(JSONList):
    model = models.INN

class ProductView(JSONRepresentation):
    model = models.Product

class ProductListView(JSONList):
    model = models.Product

class MedicineView(JSONRepresentation):
    model = models.Medicine

class MedicineListView(JSONList):
    model = models.Medicine

class ManufacturerView(JSONRepresentation):
    model = models.Manufacturer

class ManufacturerListView(JSONList):
    model = models.Manufacturer

class SiteView(JSONRepresentation):
    model = models.Site

class SiteListView(JSONList):
    model = models.Site

class SupplierView(JSONRepresentation):
    model = models.Supplier

class SupplierListView(JSONList):
    model = models.Supplier

class RegistrationView(JSONRepresentation):
    model = models.Registration

class RegistrationListView(JSONList):
    model = models.Registration

class ProcurementView(JSONRepresentation):
    model = models.Procurement

class ProcurementListView(JSONList):
    model = models.Procurement


