from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'ReadWeibo.mainapp.views.home', name='home'),
    url(r'^category/(?P<category_id>\d+)$', 'ReadWeibo.mainapp.views.home', name='category_view'),
    url(r'^set_category/$', 'ReadWeibo.mainapp.views.set_category', name='set_category'),
    url(r'^weibo_callback/$', 'ReadWeibo.account.views.weibo_callback', name='weibo_callback'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
