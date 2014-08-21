from django.conf.urls import patterns, url

from app import views

urlpatterns = patterns('',
    # /app/
    url(r'^$', views.home, name='home'),
    # /app/tasks/
    url(r'^tasks/$', views.tasks, name='tasks'),
    url(r'^tasks/incomplete/$', views.tasks_incomplete, name='tasks_incomplete'),
    url(r'^tasks/incomplete/today/$', views.tasks_incomplete_today, name='tasks_incomplete_today'),
    url(r'^tasks/incomplete/thisweek/$', views.tasks_incomplete_thisweek, name='tasks_incomplete_thisweek'),
    url(r'^tasks/incomplete/inbox/$', views.tasks_incomplete_notnow, name='tasks_incomplete_notnow'),
    url(r'^tasks/done/$', views.tasks_done, name='tasks_done'),
    # ex: /app/tasks/5/
    url(r'^tasks/(?P<task_id>\d+)/$', views.task, name='task'),
    url(r'^tasks/incomplete/(?P<task_id>\d+)/$', views.task_incomplete, name='task_incomplete'),
    url(r'^tasks/incomplete/inbox/(?P<task_id>\d+)/$', views.task_incomplete_notnow, name='task_incomplete_notnow'),
    url(r'^tasks/incomplete/today/(?P<task_id>\d+)/$', views.task_incomplete_today, name='task_incomplete_today'),
    url(r'^tasks/incomplete/thisweek/(?P<task_id>\d+)/$', views.task_incomplete_thisweek, name='task_incomplete_thisweek'),
    url(r'^tasks/done/(?P<task_id>\d+)/$', views.task_done, name='task_done'),
    # /app/meetings/
    url(r'^meetings/$', views.meetings, name='meetings'),
    url(r'^meetings/future/$', views.meetings_future, name='meetings_future'),
    url(r'^meetings/past/$', views.meetings_past, name='meetings_past'),
    # ex: /app/meetings/5/
    url(r'^meetings/(?P<meeting_id>\d+)/$', views.meeting, name='meeting'),
    url(r'^meetings/future/(?P<meeting_id>\d+)/$', views.meeting_future, name='meeting_future'),
    url(r'^meetings/past/(?P<meeting_id>\d+)/$', views.meeting_past, name='meeting_past'),
    # schedule
    url(r'^schedule/$', views.schedule, name='schedule'),
    url(r'^eventfeed/$', views.eventfeed, name='eventfeed'),
    # preferences
    url(r'^preferences/$', views.preferences, name='preferences'),
    url(r'^preferences/(?P<preference_id>\d+)/$', views.delete_preference, name='delete_preference'),
    # scheduleitems will be relayed to the corresponding tasks:
    url(r'^scheduleitems/(?P<scheduleitem_id>\d+)/$', views.scheduleitem, name='scheduleitem'),
    # ajax access from schedule
    url(r'^meetings/ajax/$', views.meetings_ajax, name='meetings_ajax'),
    # /app/terms and /app/privacy
    url(r'^terms/$', views.terms, name='terms'),
    url(r'^privacy/$', views.privacy, name='privacy'),
    # /support/
    url(r'^support/$', views.support, name='support'),
)

