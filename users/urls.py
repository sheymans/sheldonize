from django.contrib.auth.views import (
    password_change,
    password_change_done,
    password_reset,
    password_reset_done,
    password_reset_confirm,
    password_reset_complete
)

from django.conf.urls import patterns, url, include
 
from users import views

urlpatterns = patterns('',
    # /users/
    url(r'^$', views.login_v, name='login_v'),
    # /users/login/
    url(r'^login/$', views.login_v, name='login_v'),
    # /users/logout/
    url(r'^logout/$', views.logout_v, name='logout_v'),
    # /users/signup/
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    # /users/userprofile/
    url(r'^userprofile/$', views.UserProfileView.as_view(), name='userprofile'),
    # /users/wait/
    url(r'^wait/$', views.WaitView.as_view(), name='wait'),
    url(r'^wait/thanks/$', views.thanks, name='thanks'),
    # /users/invite/
    url(r'^invite/$', views.InviteView.as_view(), name='invite'),
    url(r'^invite/thanks/$', views.invite_thanks, name='invite_thanks'),
    # password stuff:
    url(r'^password/change/$', view=password_change, name='password_change'),
    url(r'^password/change/done/$', view=password_change_done, name='password_change_done'),
    url(r'^password/reset/$', view=password_reset, name='password_reset'),
    url(r'^password/reset/done/$', view=password_reset_done, name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', view=password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset_complete/$', view=password_reset_complete, name='password_reset_complete'),
    # Social login:
    url('', include('social.apps.django_app.urls', namespace='social')),
)

