from django.conf.urls import patterns, include, url

urlpatterns = patterns('reports.views',
    #url(r'^reference_report/$', 'reference_report', name='reference_report'),
    url(r'^price_grid/(?P<year>\d+)/$', 'medicine_grid', name='medicine_grid'),
    url(r'^countries_per_medicine/$', 'countries_per_medicine', name='countries_per_medicine'),
    url(r'^export/$', 'procurement_export', name='procurement_export'),
    url(r'^export/by_procurement/$', 'export_by_procurement', name='export_by_procurement'),
    url(r'^export/all_countries/$', 'export_all_countries', name='export_all_countries'),
)

