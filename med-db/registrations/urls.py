from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('registrations.views',
    url(r'^country/(?P<object_id>\d+)/$', views.CountryView.as_view(), name='country'),
    url(r'^inn/(?P<object_id>\d+)/$', views.INNView.as_view(), name='inn'),
    url(r'^product/(?P<object_id>\d+)/$', views.ProductView.as_view(), name='product'),
    url(r'^medicine/(?P<object_id>\d+)/$', views.MedicineView.as_view(), name='medicine'),
    url(r'^manufacturer/(?P<object_id>\d+)/$', views.ManufacturerView.as_view(), name='manufacturer'),
    url(r'^site/(?P<object_id>\d+)/$', views.SiteView.as_view(), name='site'),
    url(r'^supplier/(?P<object_id>\d+)/$', views.SupplierView.as_view(), name='supplier'),
    url(r'^registration/(?P<object_id>\d+)/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^procurement/(?P<object_id>\d+)/$', views.ProcurementView.as_view(), name='procurement'),
    url(r'^country/$', views.CountryListView.as_view(), name='country_list'),
    url(r'^inn/$', views.INNListView.as_view(), name='inn_list'),
    url(r'^product/$', views.ProductListView.as_view(), name='product_list'),
    url(r'^medicine/$', views.MedicineListView.as_view(), name='medicine_list'),
    url(r'^manufacturer/$', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    url(r'^site/$', views.SiteListView.as_view(), name='site_list'),
    url(r'^supplier/$', views.SupplierListView.as_view(), name='supplier_list'),
    url(r'^registration/$', views.RegistrationListView.as_view(), name='registration_list'),
    url(r'^procurement/$', views.ProcurementListView.as_view(), name='procurement_list'),
)
