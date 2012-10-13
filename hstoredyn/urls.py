from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hstoredyn.views.home', name='home'),
    # url(r'^hstoredyn/', include('hstoredyn.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^hstoredyn/$', 'hstoredyn.views.index'),
    url(r'^hstoredyn/add$', 'hstoredyn.views.add'),
    url(r'^hstoredyn/(?P<some_id>\d+)/$', 'hstoredyn.views.detail'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
