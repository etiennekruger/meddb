from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'meddb.views.home', name='home'),
    # url(r'^meddb/', include('meddb.foo.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^json/', include('registrations.urls')),
    url(r'^reports/', include('reports.urls')),
)
