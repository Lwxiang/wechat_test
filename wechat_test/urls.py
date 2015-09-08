from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wechat_test.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'wechat.views.checker'),
    url(r'^access/', 'wechat.views.get'),
    url(r'^admin/', include(admin.site.urls)),
)
