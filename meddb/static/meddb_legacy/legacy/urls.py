from django.conf.urls import patterns, include, url

urlpatterns = patterns('legacy.views',
    url(r'^medicine/$', 'medicine_list', name='medicine_list'),
    url(r'^medicine/(?P<_id>\d+)/$', 'medicine', name='medicine'),
)
