from collections import defaultdict
import dateutil.parser
from django.db.models import Q
import models
from django.http import HttpResponse, Http404
from serializers import BaseSerializer


def product(request, object_id):

    model = models.Product
    serializer = BaseSerializer()
    try:
        out = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        raise Http404
    return HttpResponse(serializer.serialize(out), content_type="application/json")


def product_list(request):

    model = models.Product
    serializer = BaseSerializer()
    out = model.objects.all()
    return HttpResponse(serializer.serialize(out), content_type="application/json")


def MedicineView(request):
    model = models.Medicine

    def remove_old_procurements(self, procurements):
        """
        Only show procurements for the latest year for each country
        """
        years = defaultdict(list)
        latest_year = {}
        new_procurements = []

        def key(procurement):
            return "%s%s" % (
                procurement["country"]["code"],
                procurement["container"]["id"]
            )

        for procurement in procurements:
            s_start_date = procurement["start_date"]
            start_date = dateutil.parser.parse(s_start_date)
            years[key(procurement)].append(start_date.year)

        for country, years in years.items():
            latest_year[country] = sorted(years, reverse=True)[0]

        for procurement in procurements:
            s_start_date = procurement["start_date"]
            start_date = dateutil.parser.parse(s_start_date)
            if start_date.year == latest_year[key(procurement)] and start_date.year >= 2011:
                new_procurements.append(procurement)

        return new_procurements


    def get_json_data(self, *args, **kwargs):
        data = super(MedicineView, self).get_json_data(*args, **kwargs)
        procurements = data["procurements"]

        new_procurements = self.remove_old_procurements(procurements)
        data["procurements"] = new_procurements

        return data


def MedicineListView(request):
    model = models.Medicine

    def queryset(self):
        search = self.request.GET.get('search', None)
        if not search:
            return self.model.objects.all()
        query = Q(ingredient__inn__name__icontains=search)
        date["procurements"] = []
        query |= Q(product__name__icontains=search)
        return self.model.objects.filter(query).distinct()

    out = serializer.serialize(model)
    return HttpResponse(out)


# def ManufacturerView(request):
#     model = models.Manufacturer
#     out = serializer.serialize(model)
#     return HttpResponse(out)
#
#
# def SupplierView(request):
#     model = models.Supplier
#     out = serializer.serialize(model)
#     return HttpResponse(out)
#
#
# def SupplierListView(request):
#     model = models.Supplier
#     out = serializer.serialize(model)
#     return HttpResponse(out)
#
#
# def ProcurementView(request):
#     model = models.Procurement
#     out = serializer.serialize(model)
#     return HttpResponse(out)
#
