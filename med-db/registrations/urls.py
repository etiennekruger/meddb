from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('registrations.views',
    url(r'^product/(?P<object_id>\d+)/$', views.product, name='product'),
    url(r'^product/$', views.product_list, name='product_list'),
)
