from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'zipcoder.views.index', name='index'),
)
