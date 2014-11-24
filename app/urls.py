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
    url(r'^tasks/incomplete/someday/$', views.tasks_incomplete_someday, name='tasks_incomplete_someday'),
    url(r'^tasks/firsttime/$', views.tasks_firstvisit, name='tasks_firstvisit'),
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
    # /app/terms and /app/privacy and /app/pricing
    url(r'^terms/$', views.terms, name='terms'),
    url(r'^privacy/$', views.privacy, name='privacy'),
    url(r'^pricing/$', views.pricing, name='pricing'),
    # /support/
    url(r'^support/$', views.support, name='support'),
    # /google/authentication/; the Google Developer Console contains
    # https://localhost:8000/app/oauth2callback TODO: also add sheldonize.com
    url(r'^oauth2callback', views.auth_return, name='auth_return'),
    url(r'^googlecalendar', views.googlecalendar, name='googlecalendar'),
    url(r'^autherror', views.auth_error, name='auth_return'),
    # Statistics
    url(r'^stats/$', views.stats_v, name='stats'),
    url(r'^stats/weekly/$', views.stats_weekly, name='stats_weekly'),
    url(r'^stats/monthly/$', views.stats_monthly, name='stats_monthly'),
    # Respond to Mailgun requests; this is posting without forms so bypass csrf
    url(r'^mailgun/$', views.mailgun, name='mailgun'),
    # Ajax to post meeting/task note
    url(r'^meetings/note/ajax/$', views.meeting_note_ajax, name='meeting_note_ajax'),
    url(r'^tasks/note/ajax/$', views.task_note_ajax, name='task_note_ajax'),
    url(r'^habits/note/ajax/$', views.habit_note_ajax, name='habit_note_ajax'),
    # Searching
    url(r'^search/$', views.search, name='search'),
    # /app/habits/
    url(r'^habits/$', views.habits, name='habits'),
    url(r'^habits/(?P<habit_id>\d+)/$', views.habit, name='habit'),

)

