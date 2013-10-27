from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #Home
    url(r'^$', 'ReadWeibo.mainapp.views.home', name='home'),

    #Weibo
    url(r'^weibo$', 'ReadWeibo.mainapp.views.show_weibos', name='weibos'),
    url(r'^weibo/category/(?P<category_id>\d+)$', 'ReadWeibo.mainapp.views.show_weibos', name='weibo_category_view'),
    url(r'^weibo/category_predict/(?P<category_id>\d+)$', 'ReadWeibo.mainapp.views.show_weibos_predict', name='weibo_category_view'),
    url(r'^set_weibo_category/$', 'ReadWeibo.mainapp.views.set_weibo_category', name='set_weibo_category'),

    #User
    url(r'^user$', 'ReadWeibo.mainapp.views.show_users', name='users'),
    url(r'^user/category/(?P<category_id>\d+)$', 'ReadWeibo.mainapp.views.show_users', name='user_category_view'),
    url(r'^user/category_predict/(?P<category_id>\d+)$', 'ReadWeibo.mainapp.views.show_users_predict', name='user_category_view'),
    url(r'^set_user_category/$', 'ReadWeibo.mainapp.views.set_user_category', name='set_user_category'),

    #User's weibos
    url(r'^user/weibos/(?P<w_uid>\d+)$', 'ReadWeibo.mainapp.views.show_user_weibos', name='user_weibo_view'),

    #Auth
    url(r'^weibo_callback$', 'ReadWeibo.account.views.weibo_callback', name='weibo_callback'),
    # Admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
