from django.conf.urls import patterns, url
 
from subscriptions import views

urlpatterns = patterns('',
    # /subscriptions/signup/
    url(r'^signup/$', views.signup_subscription, name='signup_subscription'),
    # /subscriptions/change/
    url(r'^change/$', views.change_subscription, name='change_subscription'),
    # /subscriptions/webhook/
    url(r'^webhook/$', views.webhook, name='webhook'),
)

