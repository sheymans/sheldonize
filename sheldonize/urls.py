from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'app.views.home', name='home'),
    url(r'^healthcheck/', 'app.views.healthcheck', name='healthcheck'),
    url(r'^app/', include('app.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^subscriptions/', include('subscriptions.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
