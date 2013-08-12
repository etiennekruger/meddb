from django.conf.urls import patterns, include, url

urlpatterns = patterns('reports.views',
    #url(r'^reference_report/$', 'reference_report', name='reference_report'),
    url(r'^price_grid/(?P<year>\d+)/$', 'medicine_grid', name='medicine_grid'),
    url(r'^countries_per_medicine/$', 'countries_per_medicine', name='countries_per_medicine'),
)

