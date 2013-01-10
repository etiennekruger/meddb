from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^legacy/', include('legacy.urls')),
)
