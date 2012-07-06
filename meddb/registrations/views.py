import django.utils.simplejson as json
from django import http
from django.views.generic import View
from django.db.models import Q

import models

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
        jsonp = self.request.GET.get('jsonp', False)
        if jsonp:
            return http.HttpResponse(jsonp+'('+content+');',
                                     content_type='text/javascript',
                                     **httpresponse_kwargs)            
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
        return response

class JSONRepresentation(JSONView):
    def get_json_data(self, *args, **kwargs):
        self.instance = self.model.objects.select_related().get(pk=kwargs['object_id'])
        return self.instance.as_dict()

class JSONList(JSONView):
    queryset = None
    def get_json_data(self, *args, **kwargs):
        if self.queryset == None:
            queryset = self.model.objects.all()
        else:
            queryset = self.queryset
        return [i.as_dict(minimal=True) for i in queryset.select_related()]

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
    
    @property
    def queryset(self):
        search = self.request.GET.get('search', None)
        if not search:
            return None
        return self.model.objects.filter(name__icontains=search)

class ProductView(JSONRepresentation):
    model = models.Product

class ProductListView(JSONList):
    model = models.Product

class MedicineView(JSONRepresentation):
    model = models.Medicine

class MedicineListView(JSONList):
    model = models.Medicine
    
    @property
    def queryset(self):
        search = self.request.GET.get('search', None)
        if not search:
            return self.model.objects.all()
        query = Q(ingredient__inn__name__icontains=search)
        query |= Q(product__name__icontains=search)
        return self.model.objects.filter(query)

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
