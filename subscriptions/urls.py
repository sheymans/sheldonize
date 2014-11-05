from django.conf.urls import patterns, url
 
from subscriptions import views

urlpatterns = patterns('',
    # /subscriptions/signup/
    url(r'^signup/$', views.signup_subscription, name='signup_subscription'),
    # /subscriptions/signup_student/
    url(r'^signup_student/$', views.signup_student, name='signup_student'),
    # /subscriptions/signup_donate/
    url(r'^signup_donate/$', views.signup_donate, name='signup_donate'),
    # /subscriptions/change/
    url(r'^change/$', views.change_subscription, name='change_subscription'),
    # /subscriptions/webhook/
    url(r'^webhook/$', views.webhook, name='webhook'),
)

