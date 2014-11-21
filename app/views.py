from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django_tables2 import RequestConfig
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from users.models import UserProfile, Invite

from django.contrib.auth.models import User
from models import Task, ScheduleItem, Preference, Meeting, CredentialsModel, FlowModel
from tables import TaskTable, PreferenceTable, MeetingTable
from forms import TaskForm, AddTaskForm, AddPreferenceForm, MeetingForm, AddMeetingForm
import service
import stats
import json
import arrow
import logging
import requests
# for searching with django-watson
import watson

# for parsing the bodies from emails
from django.utils.encoding import smart_str

from dateutil.parser import parse

from django.contrib.auth.decorators import login_required, user_passes_test


# Google Authentication
import httplib2
from apiclient.discovery import build
from oauth2client import xsrfutil
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage



logger = logging.getLogger(__name__)

def home(request):
    if request.user.is_authenticated():
        return redirect(tasks)
    else:
        #return render(request, "home.html", {'device_type': request.device_type, 'trial_registrations_left': trial_registrations_left, 'tasks_count': tasks_count, 'meetings_count': meetings_count, 'users_count': user_count})
        return render(request, "home.html", {'device_type': request.device_type})

# ELB needs a healthcheck returning 200
def healthcheck(request):
    free_registrations_left = service.free_registrations_left()
    user_count = User.objects.count()
    donor_count = UserProfile.objects.filter(usertype=7).count()
    return HttpResponse('<ul><li>users in system: ' + str(user_count) + '</li><li>free accounts left: ' + str(free_registrations_left) + '</li><li>donors: ' + str(donor_count)+ '</li></ul>')

# The terms of use
def terms(request):
    return render(request, "terms_of_use.html")

# The privacy policy
def privacy(request):
    return render(request, "privacy.html")

# The pricing
def pricing(request):
    return render(request, "pricing.html")

# The support
@login_required
@user_passes_test(lambda user: user.is_active, login_url="/subscriptions/signup/")
def support(request):
    if request.method == "GET":
        form = AddTaskForm()
        try:
            superuser = User.objects.get(username='support')
            # get the tasks of the support user that have as a topic this users
            # email (that's the support tasks of this user)
            current = list(Task.objects.filter(user=superuser, topic=request.user.email))
        except:
            current = None
        return render(request, "support.html", {'device_type': request.device_type, 'addtaskform': form, 'current_support_requests': current})

    elif request.method == "POST":
        success = ""
        error = "Oh. This is unexpected."
        warning = ""
        if 'new_task' in request.POST:
            form = AddTaskForm(request.POST)
            if form.is_valid():
                task_instance = form.save(commit=False)
                # TODO do not hard code this, set this in settings
                try:
                    superuser = User.objects.get(username='support')
                except ObjectDoesNotExist:
                    superuser = User.objects.create_user('support', 'stijn.heymans+support@gmail.com', 'GV@4c*yiLBge')
                    user_profile = UserProfile.objects.create(user=superuser, usertype=0)
                    user_profile.timezone = 'America/Los_Angeles'
                    user_profile.save()
                    
                task_instance.user=superuser
                task_instance.name = task_instance.name
                task_instance.topic = request.user.email
                success = "Question or issue filed to the main developers; we will get back to you soon!"
                # don't forget to save then
                task_instance.save()
            else:
                warning = "Please enter a task."
            
        if success:
            messages.add_message(request, messages.SUCCESS, success)
        elif warning:
            messages.add_message(request, messages.WARNING, warning)
        elif error:
            messages.add_message(request, messages.ERROR, error)

        return redirect_to_current(request, support)

    else:
        raise Http404
 

# what to show when in tasks:
# SHOW_TASKS = { 'incomplete': True, 'when': None }

@login_required
@user_passes_test(lambda user: user.is_active, login_url="/subscriptions/signup/")
def tasks_generic(request, tasks_view, schedule_view, show_tasks):
    if request.method == "GET":
        if show_tasks['incomplete']:
            if show_tasks['when'] and show_tasks['when'] == 'T':
                # today
                table = TaskTable(Task.objects.filter(user=request.user, done=False, when='T'))
                form = AddTaskForm()
                RequestConfig(request, paginate={"per_page": 10}).configure(table)
                return render(request, "app/tasks.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'addtaskform': form, 'what_tasks' : show_tasks})
            elif show_tasks['when'] and show_tasks['when'] == 'W':
                table = TaskTable(Task.objects.filter(user=request.user, done=False, when='W'))
                form = AddTaskForm()
                RequestConfig(request, paginate={"per_page": 10}).configure(table)
                return render(request, "app/tasks.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'addtaskform': form, 'what_tasks' : show_tasks})
            elif show_tasks['when'] and show_tasks['when'] == 'Z':
                table = TaskTable(Task.objects.filter(user=request.user, done=False, when='Z'))
                form = AddTaskForm()
                RequestConfig(request, paginate={"per_page": 10}).configure(table)
                return render(request, "app/tasks.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'addtaskform': form, 'what_tasks' : show_tasks})
            #elif show_tasks['when'] and show_tasks['when'] == 'NoTNoW':
            else:
                table = TaskTable(Task.objects.filter(user=request.user, done=False, when__isnull=True))
                form = AddTaskForm()
                RequestConfig(request, paginate={"per_page": 10}).configure(table)
                return render(request, "app/tasks.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'addtaskform': form, 'what_tasks' : show_tasks})
        #elif show_tasks['done']:
        else:
            table = TaskTable(Task.objects.filter(user=request.user, done=True))
            # Note that we do not show form for done tasks
            RequestConfig(request, paginate={"per_page": 10}).configure(table)
            return render(request, "app/tasks.html", {'table': table,'pages': [i+1 for i in range(table.paginator.num_pages)], 'what_tasks' : show_tasks})

    elif request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_tasks = Task.objects.filter(user=request.user, pk__in=pks)
        success = ""
        warning = "Please select a task first."
        error = ""
        if 'complete-marked-tasks' in request.POST and selected_tasks:
            for task in selected_tasks:
                task.done = True
                task.save()
                success = "Tasks marked as Done and moved to Archive."
        elif 'uncomplete-marked-tasks' in request.POST:
            for task in selected_tasks:
                task.done = False
                task.when = None
                task.save()
                success = "Task marked not Done and back to Inbox."
        elif 'delete-marked-tasks' in request.POST:
            if selected_tasks.exists():
                selected_tasks.delete()
                success = "Tasks deleted."
        elif 'thisweek-marked-tasks' in request.POST:
            for task in selected_tasks:
                task.when = 'W'
                task.save()
                success = "Tasks moved to This Week."
        elif 'today-marked-tasks' in request.POST:
            for task in selected_tasks:
                task.when = 'T'
                task.save()
                success = "Tasks moved to Today."
        elif 'someday-marked-tasks' in request.POST:
            for task in selected_tasks:
                task.when = 'Z'
                task.save()
                success = "Tasks moved to Someday/Maybe."
        elif 'nowhen-marked-tasks' in request.POST:
            for task in selected_tasks:
                task.when = None
                task.save()
                success = "Tasks moved to Inbox."
        elif 'new_task' in request.POST:
            warning = ""
            form = AddTaskForm(request.POST)
            if form.is_valid():
                task_instance = form.save(commit=False)
                task_instance.user=request.user
                # determine whether to also add Today/Thisweek depending on the
                # context of where the task was called
                if 'when' in show_tasks and show_tasks['when'] == 'T':
                    task_instance.when = 'T'
                    success = "Task added to Today."
                elif 'when' in show_tasks and show_tasks['when'] == 'W':
                    task_instance.when = 'W'
                    success = "Task added to This Week."
                elif 'when' in show_tasks and show_tasks['when'] == 'Z':
                    task_instance.when = 'Z'
                    success = "Task added to Someday/Maybe."
                else:
                    success = "Task added."
                # don't forget to save then
                task_instance.save()
            else:
                error = "Task could not be added."
        elif 'calculate-schedule' in request.POST:
            warning = ""
            quick_schedule(request)
            return redirect(schedule_view)
            
        if success:
            messages.add_message(request, messages.SUCCESS, success)
        elif warning:
            messages.add_message(request, messages.WARNING, warning)
        elif error:
            messages.add_message(request, messages.ERROR, error)

        return redirect_to_current(request, tasks_view)

    else:
        raise Http404
 
@login_required
def tasks_incomplete(request):
    # relay this to tasks_incomplete_notnow
    return tasks_incomplete_notnow(request)

@login_required
def tasks_incomplete_notnow(request):
    show_tasks = {'incomplete': True, 'done': False, 'when': 'NoTNoW' }
    return tasks_generic(request, tasks_incomplete_notnow, schedule, show_tasks)


@login_required
def tasks_incomplete_today(request):
    show_tasks = {'incomplete': True, 'done': False, 'when': 'T' }
    return tasks_generic(request, tasks_incomplete_today, schedule, show_tasks)

@login_required
def tasks_incomplete_thisweek(request):
    show_tasks = {'incomplete': True, 'done': False, 'when': 'W' }
    return tasks_generic(request, tasks_incomplete_thisweek, schedule, show_tasks)

@login_required
def tasks_incomplete_someday(request):
    show_tasks = {'incomplete': True, 'done': False, 'when': 'Z' }
    return tasks_generic(request, tasks_incomplete_someday, schedule, show_tasks)

@login_required
def tasks_done(request):
    show_tasks = {'incomplete': False, 'done': True, 'when': None }
    return tasks_generic(request, tasks_done, schedule, show_tasks)

@login_required
def tasks(request):
    # we just relay tasks to tasks_incomplete (we do not wish to show all
    # tasks)
    return tasks_incomplete_notnow(request)

@login_required
def tasks_firstvisit(request):
    show_tasks = {'incomplete': True, 'done': False, 'when': 'NoTNoW', 'first': True }
    return tasks_generic(request, tasks_incomplete_notnow, schedule, show_tasks)

# Single Task

@login_required
@user_passes_test(lambda user: user.userprofile.all_permissions_granted(), login_url="/subscriptions/signup/")
def task_generic(request, task_id, task_list_view, task_link):
    task = get_object_or_404(Task, pk=task_id)
    
    original_note = Task.objects.get(id=task.id).note

    # check whether this is indeed your task!
    if task.user != request.user:
        raise PermissionDenied
    
    if request.method == "GET":
        form = TaskForm(instance=task)
        return render(request, 'app/task.html', {'form': form, 'task_link': task_link, 'note': task.note, 'taskid': task.id})
    elif request.method == "POST":
        if 'delete-task' in request.POST:
            task.delete()
            messages.add_message(request, messages.SUCCESS, "Deleted task.")
            return go_back_to_previous(request, task_list_view)
        else:
            # it's a submit
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                # commit=False means the form doesn't save at this time.
                # commit defaults to True which means it normally saves.
                task_instance = form.save(commit=True)

                # add the original note (the note is not in the form but gets
                # changed in the back):
                task_instance.note = original_note
                task_instance.save()

                messages.add_message(request, messages.SUCCESS, "Updated task.")
                return go_back_to_previous(request, task_list_view)
            else:
                messages.add_message(request, messages.ERROR, "The task you tried to update is not valid. Please correct the indicated error.")
                return render(request, 'app/task.html', {'form': form})
    else:
        raise Http404


@login_required
def task_incomplete(request, task_id):
    return task_generic(request, task_id, tasks_incomplete, '/app/tasks/incomplete/')

@login_required
def task_incomplete_notnow(request, task_id):
    return task_generic(request, task_id, tasks_incomplete_notnow, '/app/tasks/incomplete/inbox/')

@login_required
def task_incomplete_today(request, task_id):
    return task_generic(request, task_id, tasks_incomplete_today, '/app/tasks/incomplete/inbox/today/')

@login_required
def task_incomplete_thisweek(request, task_id):
    return task_generic(request, task_id, tasks_incomplete_thisweek, '/app/tasks/incomplete/inbox/thisweek/')

@login_required
def task_done(request, task_id):
    return task_generic(request, task_id, tasks_done, '/app/tasks/done/')

@login_required
def task(request, task_id):
    return task_generic(request, task_id, tasks, '/app/tasks/')



### Schedule


@login_required
def quick_schedule(request):
    user_timezone = service.get_timezone(request.user)
    info = service.schedule(request.user, user_timezone)
    messages.add_message(request, messages.ERROR, info[0])
    messages.add_message(request, messages.WARNING, info[1])
    messages.add_message(request, messages.SUCCESS, info[2])

@login_required
def calculate_schedule(request):
    info = ("", "", "")
    if request.method == "POST":
        if 'calculate-schedule' in request.POST:
            # perform the actual scheduling
            user_timezone = service.get_timezone(request.user)
            info = service.schedule(request.user, user_timezone)
        elif 'delete-schedule' in request.POST:
            # trash complete schedule
            service.clear_scheduleditems(request.user)
            service.clear_externalitems(request.user)
            messages.add_message(request, messages.SUCCESS, "Schedule cleared.")
    return info
                
@login_required
@user_passes_test(lambda user: user.userprofile.all_permissions_granted(), login_url="/subscriptions/signup/")
def schedule(request):
    # Did someone ask for the google calendar?
    if request.method == "POST" and 'get-google-calendar' in request.POST:
             return redirect('/app/googlecalendar/')

    info = calculate_schedule(request)
    messages.add_message(request, messages.ERROR, info[0])
    messages.add_message(request, messages.WARNING, info[1])
    messages.add_message(request, messages.SUCCESS, info[2])
    # device type gets set by DetectMobile middleware
    # requires middle ware cannot be tested really
    if request.device_type == 'mobile': # pragma: no cover
        to_show = service.get_current_and_next_up_in_schedule(request.user)
        to_show_dict = service.get_dict_from_meetings_scheduleitems(to_show, service.get_timezone(request.user))
        current = None
        next_up = None
        if len(to_show_dict) == 2:
            current = to_show_dict[0]
            next_up = to_show_dict[1]
        elif len(to_show_dict) == 1:
            current = to_show_dict[0]
        return render(request, "app/schedule.html", {'device_type': request.device_type, 'current': current, 'next_up': next_up, 'eventfeed_url': "/app/eventfeed/"})
    else:
        return render(request, "app/schedule.html", {'device_type': request.device_type, 'task_link' : '/app/tasks/incomplete/', 'what_tasks' : '', 'eventfeed_url': "/app/eventfeed/"})


### Eventfeed


@login_required
@user_passes_test(lambda user: user.is_active, login_url="/subscriptions/signup/")
def eventfeed(request):
    if request.method == "GET":
        user_timezone = service.get_timezone(request.user)
        fr = arrow.get(request.GET.get('start')).to(user_timezone)
        to = arrow.get(request.GET.get('end')).to(user_timezone)

        tasks = service.get_tasks_between_from_and_to(request.user, fr, to)
        meetings = service.get_meetings_between_from_and_to(request.user, fr, to)
        scheduleis = service.get_scheduleitems_between_from_and_to(request.user, fr, to)

        deadlines = service.tasks_2_dict(tasks, user_timezone)
        meeting_items = service.meetings_2_dict(meetings, user_timezone)
        scheduleitems = service.scheduleitems_2_dict(scheduleis, user_timezone)

        all_to_show = list(deadlines)
        all_to_show.extend(meeting_items)
        all_to_show.extend(scheduleitems)
        return HttpResponse(json.dumps(all_to_show), content_type="application/json")

    else:
        raise Http404

### Preference

@login_required
@user_passes_test(lambda user: user.is_active, login_url="/subscriptions/signup/")
def delete_preference(request, preference_id):
    # Delete a preference if someone hits the right ID
    preference = get_object_or_404(Preference, pk=preference_id)

    # check whether this is indeed yours
    if preference.user != request.user:
        raise PermissionDenied

    preference.delete()
    return redirect(preferences)

@login_required
@user_passes_test(lambda user: user.userprofile.all_permissions_granted(), login_url="/subscriptions/signup/")
def preferences(request):
    # show all preferences if GET
    if request.method == "GET":
            table = PreferenceTable(Preference.objects.filter(user=request.user))
            form = AddPreferenceForm()
            RequestConfig(request, paginate={"per_page": 10}).configure(table)
            return render(request, "app/preferences.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'addpreferenceform': form})
    # add a preference if POST
    elif request.method == "POST":
        success = ""
        error = ""
        if 'new_preference' in request.POST:
            form = AddPreferenceForm(request.POST)
            if form.is_valid():
                preference_instance = form.save(commit=False)
                preference_instance.user=request.user
                preference_instance.save()
                success = "Preference added."
            else:
                error = "Preference could not be added."

            
        if success:
            messages.add_message(request, messages.SUCCESS, success)
        elif error:
            messages.add_message(request, messages.ERROR, error)
        return redirect(preferences)

    else:
        raise Http404


### Meeting List

@login_required
@user_passes_test(lambda user: user.is_active, login_url="/subscriptions/signup/")
def meetings_generic(request, meetings_view, schedule_view, show_future_meetings, show_past_meetings):
    if request.method == "GET":
        if show_future_meetings:
            table = MeetingTable(service.get_future_meetings(request.user))
            form = AddMeetingForm()
            RequestConfig(request, paginate={"per_page": 10}).configure(table)
            return render(request, "app/meetings.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'addmeetingform': form, 'what_meetings' : 'future'})
        #elif show_past_meetings:
        else:
            table = MeetingTable(service.get_past_meetings(request.user))
            RequestConfig(request, paginate={"per_page": 10}).configure(table)
            # When showing past meetings we do not show form to add meetings
            return render(request, "app/meetings.html", {'table': table, 'pages': [i+1 for i in range(table.paginator.num_pages)], 'what_meetings' : 'past'})

    elif request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_meetings = Meeting.objects.filter(user=request.user, pk__in=pks)
        success = ""
        warning = "Please select a meeting first."
        error = ""
        if 'delete-marked-meetings' in request.POST and selected_meetings:
            if selected_meetings:
                selected_meetings.delete()
                success = "Meetings deleted"
        elif 'new_meeting' in request.POST:
            warning = ""
            form = AddMeetingForm(request.POST)
            if form.is_valid():
                # we just have a name from this form
                data = form.cleaned_data
                name = data['name']
                # we are going to create a one hour meeting (now)
                timezone = service.get_timezone(request.user)
                start = service.nearest_quarter_time(arrow.utcnow().to(timezone))
                end = start.replace(hours=+1)
                meeting = Meeting.objects.create(user=request.user, name=name, start=start.datetime, end=end.datetime)
                meeting.save()
                success = "Meeting added."
            else:
                error = "Meeting could not be added."

        elif 'go-to-schedule' in request.POST:
            return redirect(schedule_view)
            
        if success:
            messages.add_message(request, messages.SUCCESS, success)
        elif warning:
            messages.add_message(request, messages.WARNING, warning)
        elif error:
            messages.add_message(request, messages.ERROR, error)
        return redirect_to_current(request, meetings_view)

    else:
        raise Http404
 
@login_required
def meetings_future(request):
    return meetings_generic(request, meetings_future, schedule, True, False)
 
@login_required
def meetings_past(request):
    return meetings_generic(request, meetings_past, schedule, False, True)

@login_required
def meetings(request):
    return meetings_future(request)


# Single Meeting

@login_required
@user_passes_test(lambda user: user.userprofile.all_permissions_granted(), login_url="/subscriptions/signup/")
def meeting_generic(request, meeting_id, meeting_list_view, meeting_link):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # is it foreign or not
    foreign_marker = meeting.foreign
    original_note = Meeting.objects.get(id=meeting.id).note

    # check whether this is indeed yours
    if meeting.user != request.user:
        raise PermissionDenied

    if request.method == "GET":
        form = MeetingForm(instance=meeting)
        return render(request, 'app/meeting.html', {'form': form, 'meeting_link': meeting_link, 'note': meeting.note, 'meetingid': meeting.id, 'foreign': meeting.foreign})
    elif request.method == "POST":
        if 'delete-meeting' in request.POST:
            meeting.delete()
            messages.add_message(request, messages.SUCCESS, "Deleted meeting.")
            return go_back_to_previous(request, meeting_list_view)
        else:
            form = MeetingForm(request.POST, instance=meeting)
            if form.is_valid():
                # Do not forget to also set the foreign label (the form does
                # not have that field, so it would be set to None if you do it
                # explicitly).
                meeting_instance = form.save(commit=True)
                # if it is external (0 is Google)
                if foreign_marker == 0:
                    meeting_instance.foreign = foreign_marker
                # Make sure to put the meeting_instance note back to note (the
                # if the form's note was changed in the meantime since loading
                # the form, we would wronfully overwrite the new note with the
                # old note). And you cannot just take meeting.note (you have to
                # get it from the database)
                meeting_instance.note = original_note

                # and now save
                meeting_instance.save()
                messages.add_message(request, messages.SUCCESS, "Saved meeting.")
                return go_back_to_previous(request, meeting_list_view)
            else:
                messages.add_message(request, messages.ERROR, "The meeting you tried to save is not valid. Please correct the indicated error.")
                return render(request, 'app/meeting.html', {'form': form})
    else:
        raise Http404


@login_required
def meeting_future(request, meeting_id):
    return meeting_generic(request, meeting_id, meetings_future, '/app/meetings/future/')

@login_required
def meeting_past(request, meeting_id):
    return meeting_generic(request, meeting_id, meetings_past, '/app/meetings/past/')

@login_required
def meeting(request, meeting_id):
    return meeting_generic(request, meeting_id, meetings, '/app/meetings/')


### AJAX for things arriving from the Schedule

@login_required
def meetings_ajax(request):
    if request.method == "POST":
        name_meeting = request.POST["name"]
        start = request.POST["start"]
        end = request.POST["end"]
        timezone = service.get_timezone(request.user)
        if "id" in request.POST:
            id = request.POST["id"]
        else:
            id = None
        # we are using dateutil.parser to parse this, arrow is not able to
        # recognize the format fullcalendar sends
        start_new = arrow.get(parse(start)).replace(tzinfo=timezone)
        end_new = arrow.get(parse(end)).replace(tzinfo=timezone)

        if id:
            meeting = Meeting.objects.get(id=id)
            meeting.start = start_new.datetime
            meeting.end = end_new.datetime
        else:
            meeting = Meeting.objects.create(user=request.user, name=name_meeting, start=start_new.datetime, end=end_new.datetime)

        meeting.user = request.user
        meeting.save()

        jmeetings = service.meetings_2_dict([meeting], timezone)
        return HttpResponse(json.dumps(jmeetings[0]), content_type="application/json")

    else:
        raise Http404



### Scheduleitem ID: relay to task:

@login_required
def scheduleitem(request, scheduleitem_id):
    if scheduleitem_id:
        scheduleitem= ScheduleItem.objects.get(id=scheduleitem_id)
        if scheduleitem:
            task = scheduleitem.task
            return redirect("/app/tasks/" + str(task.id) + "/")


### Utilities:

# requires middleware to set previous_url, so with "pragma" we skip irrelevant
# lines
def go_back_to_previous(request, default_view):
    """If request.session has a previous_url set, redirect to that one, otherwise fall back to default_view."""
    previous_url = default_view
    if request.session and 'previous_url' in request.session: # pragma: no cover
        previous_url = request.session['previous_url']
    return redirect(previous_url)

def redirect_to_current(request, default_view):
    """If request.session has a current_url set, redirect to that one, otherwise fall back to default_view."""
    current_url = default_view
    if request.session and 'current_url' in request.session: # pragma: no cover
        current_url = request.session['current_url']
    return redirect(current_url)



### Google Authentication

@login_required
def googlecalendar(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True or credential.access_token_expired == True:
        if FlowModel.objects.filter(id=request.user).exists():
            # there is already a flow model for this user
            # get it
            flow_model = FlowModel.objects.get(id=request.user)
        else:
            # create it
            flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_CLIENT_ID,
                                       client_secret=settings.GOOGLE_CLIENT_SECRET,
                                       scope=settings.GOOGLE_SCOPE,
                                       redirect_uri=settings.GOOGLE_REDIRECT_URI)
            flow_model = FlowModel.objects.create(id=request.user, flow=flow)

        flow_model.flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user)
        flow_model.save()

        authorize_url = flow_model.flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        cal_service = build('calendar', 'v3', http=http)

        calendar_list = cal_service.calendarList().list().execute()
        chosen_calendars = []
        for calendar_list_entry in calendar_list['items']:
            if 'selected' in calendar_list_entry:
                chosen_calendars.append((calendar_list_entry['id'], calendar_list_entry['summary']))

        events = []
        now = arrow.utcnow()
        past8 = now.replace(days=-8)
        next8=now.replace(days=+8)
        # First Remove all foreign events for that user
        Meeting.objects.filter(user=request.user, foreign=0).delete()
        for item in chosen_calendars:
            calendar_id = item[0] 
            summary = item[1]
            events = cal_service.events().list(calendarId=calendar_id, singleEvents=True, timeMin=past8.datetime.isoformat(), timeMax=next8.datetime.isoformat()).execute()
            info = service.save_google_events(request.user, events, summary)
            messages.add_message(request, messages.ERROR, info[0])
            messages.add_message(request, messages.WARNING, info[1])
            messages.add_message(request, messages.SUCCESS, info[2])

    return redirect('/app/schedule/')

@login_required
def auth_return(request):
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], request.user):
        return auth_error(request)
    try:
        flow = FlowModel.objects.get(id=request.user).flow
    except:
        return auth_error(request)

    try:
        credential = flow.step2_exchange(request.REQUEST)
        storage = Storage(CredentialsModel, 'id', request.user, 'credential')
        storage.put(credential)
    except:
        return auth_error(request)
    # go back to google calendar to then get the google calendar data
    return redirect('/app/googlecalendar/')

@login_required
def auth_error(request):
    return render(request, "auth_error.html")

def clean_up_authentication(user):
    # we do this at logout
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    storage.delete()
    FlowModel.objects.filter(id=user).delete()
    CredentialsModel.objects.filter(id=user).delete()

## Statistics

@login_required
def stats_v(request):
    return redirect(stats_weekly)

@login_required
def stats_weekly(request):
    if request.method == "GET":
        data = stats.collect_weekly_todos(request.user)
        # now turn it into something that we can use in the html
        if not data:
            return render(request, "app/stats.html", {'stats_data': None, 'stats_when': 'weekly'})

        start = data[0]
        end = data[1]
        maximum = data[2]
        todo_numbers = data[3]

        stats_data = []
        
        while start <= end:
            item = {}
            item['year'] = end[0]
            item['weeknumber'] = end[1]
            if (end[0], end[1]) in todo_numbers:
                item['total'] = todo_numbers[(end[0], end[1])]
            else:
                item['total'] = 0
            item['percentage'] = (item['total'] / float(maximum))*100
            stats_data.append(item.copy())

            # run from end to start AND only for 1 year!!! (otherwise we have
            # to know the number of weeks in the previous year, and we're not
            # into that)
            if end[1] - 1 > 0:
                end = (end[0], end[1] - 1, end[2])
            else:
                # done
                break

        return render(request, "app/stats.html", {'stats_data': stats_data, 'stats_when': 'weekly'})

@login_required
def stats_monthly(request):
    if request.method == "GET":
        data = stats.collect_monthly_todos(request.user)
        # now turn it into something that we can use in the html
        if not data:
            return render(request, "app/stats.html", {'stats_data': None, 'stats_when': 'monthly'})

        start = data[0]
        end = data[1]
        maximum = data[2]
        todo_numbers = data[3]

        stats_data = []
        
        while start <= end:
            item = {}
            item['year'] = end[0]
            item['month'] = end[1]
            if (end[0], end[1]) in todo_numbers:
                item['total'] = todo_numbers[(end[0], end[1])]
            else:
                item['total'] = 0
            item['percentage'] = (item['total'] / float(maximum))*100
            stats_data.append(item.copy())

            # run from end to start AND only for 1 year!!! (otherwise we have
            # to know the number of weeks in the previous year, and we're not
            # into that)
            if end[1] - 1 > 0:
                end = (end[0], end[1] - 1)
            elif end[1] == 1:
                # minus the year with 1 and set month to 12
                end = (end[0] - 1, 12)
            else:
                # done
                break

        for item in stats_data:
            if item['month'] == 1:
                item['month'] = 'Jan'
            elif item['month'] == 2:
                item['month'] = 'Feb'
            elif item['month'] == 3:
                item['month'] = 'Mar'
            elif item['month'] == 4:
                item['month'] = 'Apr'
            elif item['month'] == 5:
                item['month'] = 'May'
            elif item['month'] == 6:
                item['month'] = 'Jun'
            elif item['month'] == 7:
                item['month'] = 'Jul'
            elif item['month'] == 8:
                item['month'] = 'Aug'
            elif item['month'] == 9:
                item['month'] = 'Sep'
            elif item['month'] == 10:
                item['month'] = 'Oct'
            elif item['month'] == 11:
                item['month'] = 'Nov'
            elif item['month'] == 12:
                item['month'] = 'Dec'

        return render(request, "app/stats.html", {'stats_data': stats_data, 'stats_when': 'monthly'})


# Responding to Mailgun

@csrf_exempt
def mailgun(request):
     if request.method == 'POST':
        sender    = request.POST.get('sender')
        subject   = request.POST.get('subject', '')
        body_plain = request.POST.get('body-plain', '')

         # let's find that sender in our users
        if User.objects.filter(email=sender).exists():
            user_sender = User.objects.get(email=sender)
            short_task = (subject[:135] + '..') if len(subject) > 139 else subject


            today = True if "#today" in short_task else False
            thisweek = True if "#thisweek" in short_task else False

            # now create a task:
            if today:
                short_task = short_task.replace("#today", "", 1)
                task = Task.objects.create(user=user_sender, name=short_task, topic="via email", done=False, when='T')
            elif thisweek:
                short_task = short_task.replace("#thisweek", "", 1)
                task = Task.objects.create(user=user_sender, name=short_task, topic="via email", done=False, when='W')
            else:
                task = Task.objects.create(user=user_sender, name=short_task, topic="via email", done=False)

            if body_plain:
                # body_plain is unicode, we make ascii out if it
                task.note = smart_str(body_plain)

            task.save()

     # Mailgun wants to see 2xx, otherwise it will make another attempt in 5 minutes
     return HttpResponse('OK')

# Ajax for saving a note

@login_required
def meeting_note_ajax(request):
    if request.method == "POST":
        note = request.POST["note"]
        id = request.POST["id"]

        if id:
            meeting = Meeting.objects.get(id=id)

            # check whether this is indeed yours
            if meeting.user != request.user:
                raise PermissionDenied

            meeting.note = note

        meeting.save()

        return HttpResponse(json.dumps({'id': id}), content_type="application/json")

    else:
        raise Http404

@login_required
def task_note_ajax(request):
    if request.method == "POST":
        note = request.POST["note"]
        id = request.POST["id"]

        if id:
            task = Task.objects.get(id=id)

            # check whether this is indeed yours
            if task.user != request.user:
                raise PermissionDenied

            task.note = note

        task.save()

        return HttpResponse(json.dumps({'id': id}), content_type="application/json")

    else:
        raise Http404

# Search

@login_required
def search(request):
    if request.method == "GET":
        if "q" in request.GET:
            query = request.GET["q"]
            # Make sure we only look for the current user
            #search_results = watson.search(query, models=(Task.objects.filter(user=request.user), Meeting.objects.filter(user=request.user),))
            tasks_open_search_results = watson.search(query, models=(Task.objects.filter(user=request.user, done=False),))
            tasks_closed_search_results = watson.search(query, models=(Task.objects.filter(user=request.user, done=True),))
            meetings_search_results = watson.search(query, models=(Meeting.objects.filter(user=request.user),))

            return render(request, "app/search.html", {'tasks_open_search_results': tasks_open_search_results,
                'tasks_closed_search_results': tasks_closed_search_results,
                'meetings_search_results': meetings_search_results})
        else:
            return render(request, "app/search.html")
    else:
        raise Http404






