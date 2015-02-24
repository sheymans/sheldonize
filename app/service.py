from models import Task, ScheduleItem, Preference, Meeting, Habit, Project
from users.models import UserProfile
import time
import datetime
import eventcolors
from django.db.models import Q
from math import ceil
import logging
import parameters

import engine.engine as e

import arrow

# for unicode imports from google calendar
from django.utils.encoding import smart_str

logger = logging.getLogger(__name__)

def tasks_2_dict(tasks, user_timezone):
    result  = []
    for task in tasks:
        if task.due:
            start = arrow.get(task.due).to(user_timezone)
            # calculate whether due is in past
            now = arrow.utcnow().to(user_timezone)
            in_past = now > start

            jso = {}
            # Construction of events as
            # http://arshaw.com/fullcalendar/docs2/event_data/Event_Object/
            jso["id"] = task.id
            jso["title"] = task.name
            jso["url"] = "/app/tasks/modal/update/" + str(task.id) + "/"
            # send ISO08601 back to front-end
            jso["start"] = start.datetime.isoformat()
            jso["end"] = (start.datetime + datetime.timedelta(minutes=30)).isoformat()
            
            if in_past and not task.done:
                # only color red (deadline late) if it is late and the task is
                # not done yet
                jso["color"] = eventcolors.deadline_late["color"]
            elif task.done:
                # if the done date is set
                jso["color"] = eventcolors.deadline_inpast["color"]
            else:
                jso["color"] = eventcolors.deadline["color"]
            jso["textColor"] = eventcolors.deadline["textColor"]
            jso["editable"] = False
            jso["eventStartEditable"] = False
            jso["eventDurationEditable"] = False
            result.append(jso.copy())
        # also add the same task if it has a done_date:
        if task.done_date:
            start = arrow.get(task.done_date).to(user_timezone)
            now = arrow.utcnow().to(user_timezone)

            jso = {}
            jso["id"] = task.id
            jso["title"] = "(done) " + smart_str(task.name)
            jso["url"] = "/app/tasks/modal/update/" + str(task.id) + "/"
            # send ISO08601 back to front-end
            jso["start"] = start.datetime.isoformat()
            jso["end"] = (start.datetime + datetime.timedelta(minutes=30)).isoformat()
            if task.habit:
                jso["color"] = eventcolors.habit_done["color"]
                jso["textColor"] = eventcolors.habit_done["textColor"]
            else:
                jso["color"] = eventcolors.deadline_done["color"]
                jso["textColor"] = eventcolors.deadline_done["textColor"]
            jso["editable"] = False
            jso["eventStartEditable"] = False
            jso["eventDurationEditable"] = False
            result.append(jso.copy())

    return result

def meetings_2_dict(meetings, user_timezone):
    result  = []
    counter = 0
    for meeting in meetings:
        start = arrow.get(meeting.start).to(user_timezone)
        end = arrow.get(meeting.end).to(user_timezone)
        # calculate whether end is in past
        now = arrow.utcnow().to(user_timezone)
        in_past = now > end

        jso = {}
        # Construction of events as
        # http://arshaw.com/fullcalendar/docs2/event_data/Event_Object/

        # TODO do we need unique IDs for repeating meetings?? or is it fine if
        # the ID is the same. I think it is fine, it causes the meetings to
        # nicely move together on the schedule
        jso["id"] = meeting.id
        if meeting.repeat is not None:
            jso["title"] = "<span class=\"glyphicon glyphicon-repeat\"></span>&nbsp;&nbsp;" + meeting.name 
        elif meeting.foreign is not None:
            jso["title"] = "<span class=\"glyphicon glyphicon-cloud-download\"></span>&nbsp;&nbsp;" + meeting.name 
        else:
            jso["title"] = meeting.name
        jso["url"] = "/app/meetings/modal/update/" + str(meeting.id) + "/"
        # send ISO08601 back to front-end
        jso["start"] = start.datetime.isoformat()
        jso["end"] = end.datetime.isoformat()
        if meeting.foreign is not None and in_past:
            jso["color"] = eventcolors.meeting_foreign_past["color"]
        elif meeting.foreign is not None:
            jso["color"] = eventcolors.meeting_foreign["color"]
        elif in_past:
            jso["color"] = eventcolors.meeting_past["color"]
        else:
            jso["color"] = eventcolors.meeting["color"]
        jso["textColor"] = eventcolors.meeting["textColor"]
        jso["editable"] = True
        jso["eventStartEditable"] = True
        jso["eventDurationEditable"] = True
        result.append(jso.copy())
    return result

def find_root_projects(projects):
    """
    Find the projects that are not part of any project.
    """
    result = []
    for project in projects:
        if not project.part_of:
            result.append(project)
    return result

def create_text_link_project(project):
    return "<a href='/app/projects/modal/update/" + str(project.id) +"/' class='fm-update' data-fm-callback='reload'>" + project.name + "</a>"

def create_text_link_task(task, user_timezone):
    due_date = ""
    too_late_class = ""
    if task.due:
        due_date = arrow.get(task.due).to(user_timezone)
        now = arrow.utcnow().to(user_timezone)
        in_past = now > due_date
        if in_past:
            too_late_class = "toolate"

    base = ""
    if task.when == 'T' or task.when == 'W':
        base = "<a href='/app/tasks/modal/update/" + str(task.id) +"/' class='fm-update " + too_late_class + "'  data-fm-callback='reload'>" + task.name + "</a>"
    else:
        # not yet specifically determined time, so greyed out
        base = "<a href='/app/tasks/modal/update/" + str(task.id) +"/' class='fm-update greylink " + too_late_class + "' data-fm-callback='reload'>" + task.name + "</a>"
    if task.due:
        base += "&nbsp;&nbsp;(<i>" + str(due_date.humanize()) + "</i>)"
    return base

def project_2_dict(project, all_projects, user_timezone):
    """
    Get the children of the project and create json.
    """
    children = []
    for p in all_projects:
        if p.part_of and p.part_of.id == project.id:
            # then p is a child
            children.append(p)
            # and remove it from all_projects to avoid cycles
            all_projects.remove(p)

    # also add any tasks that are part of this project, to the children:
    for t in Task.objects.filter(part_of_id=project.id,done=False):
        children.append(t)

    jso = {}
    jso["id"] = project.id
    text_link = create_text_link_project(project)
    jso["text"] = text_link
    jso["icon"] = "glyphicon glyphicon-folder-close"
    if children:
        jso["children"] = []
        for c in children:
            if isinstance(c, Project):
                jso["children"].append(project_2_dict(c, all_projects, user_timezone))
            else: # it's a task
                text_link = create_text_link_task(c, user_timezone)
                jso["children"].append({"text": text_link , "icon": "glyphicon glyphicon-leaf" } )
    return jso

def projects_2_dict(projects, user_timezone):
    result = []
    all_projects = list(projects)
    roots = find_root_projects(all_projects)
    for project in roots:
        result.append(project_2_dict(project, all_projects, user_timezone))
    return result


def scheduleitems_2_dict(schedule_items, user_timezone):
    result = []
    for item in schedule_items:
        start = arrow.get(item.from_date).to(user_timezone)
        end = arrow.get(item.to_date).to(user_timezone)
        jso = {}
        jso["id"] = item.id
        if item.status == 0:
            jso["title"] = smart_str(item.task.name)
            jso["color"] = eventcolors.scheduleditem["color"]
        elif item.status == 1:
            # too short
            jso["title"] = "(short) " + smart_str(item.task.name)
            jso["color"] = eventcolors.scheduleditem_tooshort["color"]
        elif item.status == 2:
            # too late
            jso["title"] = "(late) " + smart_str(item.task.name)
            jso["color"] = eventcolors.scheduleditem_toolate["color"]
        # now add priority if there is one:
        if item.task.priority:
            jso["title" ] = jso["title"] + " [" + smart_str(item.task.priority) + "]"
        jso["url"] = "/app/tasks/modal/update/" + str(item.task.id) + "/"
        # send ISO08601 back to front-end
        jso["start"] = start.datetime.isoformat()
        difference = end - start
        if difference.seconds <= 900: # less than 15 minutes, then make it into 30 minutes
            jso["end"] = (start.datetime + datetime.timedelta(minutes=30)).isoformat()
        else:
            jso["end"] = end.datetime.isoformat()
        jso["textColor"] = eventcolors.scheduleditem["textColor"]
        # For schedule items that come from tasks that come from habit, we
        # always use a particuluar color:
        if item.task.habit:
            jso["color"] = eventcolors.habit["color"]
        jso["editable"] = False
        jso["eventStartEditable"] = False
        jso["eventDurationEditable"] = False
        result.append(jso.copy())
    return result

def get_dict_from_meetings_scheduleitems(items, user_timezone):
    result = []
    for i in items:
        if isinstance(i, ScheduleItem):
            result.append({'type': i.get_cname(), 'url': '/app/tasks/' + str(i.task.id) +'/', 'name': i.task.name, 'from': arrow.get(i.from_date).to(user_timezone).format("DD MMM hh:mm a"), 'to': arrow.get(i.to_date).to(user_timezone).format("DD MMM hh:mm a")})
        elif isinstance(i, Meeting):
            result.append({'type': i.get_cname(), 'name': i.name,'url': '/app/meetings/' + str(i.id) +'/', 'from': arrow.get(i.start).to(user_timezone).format("DD MMM hh:mm a"), 'to': arrow.get(i.end).to(user_timezone).format("DD MMM hh:mm a")})
    return result


def get_tasks_to_schedule(user, from_arrow, user_timezone):
    """Get all tasks from Tasks that need to be send to the scheduler."""
    tasks_thisweek = Q(when='W')
    tasks_today = Q(when='T')
    tasks_not_done = Q(done=False)
    start_arrow = from_arrow.to(user_timezone)
    #tasks = Task.objects.all()
    #for task in tasks:
    #    print task.due
    #    if task.due:
    #        print task.due > start_arrow.datetime
    #        print task.due.tzinfo
    #        print "saved timezone ", task.timezone
    tasks_future = Q(due__gt=start_arrow.datetime) | Q(due__isnull=True)
    return Task.objects.filter((tasks_thisweek | tasks_today) & tasks_not_done & tasks_future, user=user)

def get_tasks_between_from_and_to(user, from_arrow, to_arrow):

    tasks_due = Q(due__gt=from_arrow.datetime) & Q(due__lt=to_arrow.datetime)
    tasks_done = Q(done_date__isnull=False) & Q(done_date__gt=from_arrow.datetime) & Q(done_date__lt=to_arrow.datetime)
    tasks_query = tasks_due | tasks_done
    # TODO should the order first be user for faster SQL?
    return Task.objects.filter(tasks_query, user=user)

def get_scheduleitems_between_from_and_to(user, from_arrow, to_arrow):

    items_query_to_date = Q(to_date__gt=from_arrow.datetime) & Q(to_date__lt=to_arrow.datetime)
    items_query_from_date = Q(from_date__gt=from_arrow.datetime) & Q(from_date__lt=to_arrow.datetime)

    items_query = items_query_to_date | items_query_from_date

    return ScheduleItem.objects.filter(items_query, user=user)


def is_working_day(preferences, local_arrow):
    # local_arrow is local arrow datetime
    weekday = local_arrow.weekday()
    for pref in preferences:
        if pref.day == weekday:
            return True
    return False

def add_recurrent_meetings(meetings, from_arrow, to_arrow, preferences):
    result = []
    for m in meetings:
        if m.repeat is not None:
            if m.repeat == 0:
                # daily
                f = from_arrow
                e = to_arrow.replace(days=+1)
                while f <= e:
                    new_start = m.start.replace(year=f.year, month=f.month, day=f.day)
                    # make sure that the new_end appropriately increases the
                    # days as well (if we go over 00hours)
                    diff = (m.end - m.start)
                    new_end = new_start + diff
                    # do not use create (taht creates an object in the
                    # database)
                    new_m = Meeting(id=m.id, user=m.user, name=m.name, start=new_start, end=new_end, repeat=m.repeat)
                    result.append(new_m)
                    # update f
                    f = f.replace(days=+1)
            elif m.repeat == 1:
                # every work day
                f = from_arrow
                e = to_arrow.replace(days=+1)
                while f <= e:
                    new_start = m.start.replace(year=f.year, month=f.month, day=f.day)
                    local_start = arrow.get(new_start).to(m.user.userprofile.timezone)
                    if is_working_day(preferences, local_start):
                        #new_start = m.start.replace(year=f.year, month=f.month, day=f.day)
                        diff = (m.end - m.start)
                        new_end = new_start + diff
                        new_m = Meeting(id=m.id, user=m.user, name=m.name, start=new_start, end=new_end, repeat=m.repeat)
                        result.append(new_m)
                    # always move day further of course
                    f = f.replace(days=+1)

            elif m.repeat == 2:
                # weekly
                f = from_arrow
                e = to_arrow.replace(days=+1)
                while f <= e:
                    if f.weekday() == m.start.weekday():
                        new_start = m.start.replace(year=f.year, month=f.month, day=f.day)
                        diff = (m.end - m.start)
                        new_end = new_start + diff
                        new_m = Meeting(id=m.id, user=m.user, name=m.name, start=new_start, end=new_end, repeat=m.repeat)
                        result.append(new_m)
                    # always move day further of course
                    f = f.replace(days=+1)

            elif m.repeat == 3:
                # every other week
                f = from_arrow
                e = to_arrow.replace(days=+1)
                while f <= e:
                    if f.weekday() == m.start.weekday():
                        # week_offset will be a multiple of 7
                        week_offset = (f - m.start).days
                        # if week_offset is dividable by 2 it is bi-weekly
                        if week_offset % 2 == 0:
                            new_start = m.start.replace(year=f.year, month=f.month, day=f.day)
                            diff = (m.end - m.start)
                            new_end = new_start + diff
                            new_m = Meeting(id=m.id, user=m.user, name=m.name, start=new_start, end=new_end, repeat=m.repeat)
                            result.append(new_m)
                    # always move day further of course
                    f = f.replace(days=+1)

        else:
            result.append(m)

    return result

def get_meetings_between_from_and_to(user, from_arrow, to_arrow):
    # from_arrow and to_arrow are already assumed to be in the correct (local
    # to user) timezone
    meetings_query_end = Q(end__gt=from_arrow.datetime) & Q(end__lt=to_arrow.datetime)
    meetings_query_start = Q(start__gt=from_arrow.datetime) & Q(start__lt=to_arrow.datetime)
    meetings_repeat = Q(repeat__isnull=False)

    meetings_query = meetings_query_start | meetings_query_end | meetings_repeat

    # do the query
    meetings = Meeting.objects.filter(meetings_query, user=user)

    preferences = Preference.objects.filter(user=user)
    meetings = add_recurrent_meetings(meetings, from_arrow, to_arrow, preferences)

    return meetings

def get_meetings_to_schedule(user, from_arrow, user_timezone):
    """Get all meetings from Meeting that need to be send to the scheduler."""
    start_arrow = from_arrow.to(user_timezone)
    # limit meetings to 7 days from now (that should be always fine,
    # independent of what you said for this week)
    end_arrow = start_arrow.replace(days=+8)

    return get_meetings_between_from_and_to(user, start_arrow, end_arrow)

def get_future_meetings(user):
    user_timezone = get_timezone(user)
    now = arrow.utcnow().to(user_timezone)
    meetings_future = Q(end__gt=now.datetime)
    meetings_repeat = Q(repeat__isnull=False)
    return Meeting.objects.filter( meetings_future | meetings_repeat, user=user )

def get_future_scheduleitems(user):
    user_timezone = get_timezone(user)
    now = arrow.utcnow().to(user_timezone)
    scheduleitems_future = Q(to_date__gt=now.datetime)
    return ScheduleItem.objects.filter( scheduleitems_future, user=user )

def get_past_meetings(user):
    user_timezone = get_timezone(user)
    now = arrow.utcnow().to(user_timezone)
    meetings_past = Q(end__lt=now.datetime)
    meetings_norepeat = Q(repeat__isnull=True)
    return Meeting.objects.filter( meetings_past & meetings_norepeat, user=user )


def get_quarters_for_date_with_start(date_datetime, start_arrow):
    """
    Returns how many 15-minute blocks the due date is from now.
    """
    # we cut away seconds/microseconds from the things to compare 
    diff =  date_datetime.replace(second=0, microsecond=0) - start_arrow.replace(second=0, microsecond=0).datetime
    # diff is now a timedelta which only supports days and seconds
    total_minutes_in_diff = diff.days*24*60 + diff.seconds/60.0
    # round total_minutes_in_diff to quarter:
    return get_quarters_from_minutes(total_minutes_in_diff)

def get_quarters_from_minutes(minutes):
    """
    Turn minutes into quarters.
    """
    quarters_rough = float(minutes)/15
    return int(ceil(quarters_rough))


def tasks_to_engine(tasks, start_arrow):
    """
    Transform Task objects to a list of tasks suitable for the engine:
    tasks = { "123" : { "when": 0, "comes_after": "123", "due": 4, "duration": 5},
                    "345" : { "when": 1, "comes_after": "123", "due": 50, "duration": 10}}
    """
    engine_tasks = {}
    for task in tasks:
        task_details = {}
        
        if task.when=='T':
            task_details["when"]=0
        elif task.when=='W':
            task_details["when"]=1

        if task.comes_after:
            task_details["comes_after"] = task.comes_after.id

        if task.due:
            due_quarters = get_quarters_for_date_with_start(task.due, start_arrow)
            if due_quarters > 0:
                task_details["due"]=due_quarters

        if task.duration:
            task_details["duration"] = get_quarters_from_minutes(task.duration)

        if task.priority:
            if task.priority == 'A':
                task_details["priority"] = 0
            elif task.priority == 'B':
                task_details["priority"] = 1
            elif task.priority == 'C':
                task_details["priority"] = 2
            else:
                task_details["priority"] = 3

        engine_tasks[task.id] = task_details
    return engine_tasks

def meetings_to_engine(meetings, start_arrow):
    engine_meetings = []
    for meeting in meetings:
        if meeting.start and meeting.end:
            start_quarters = get_quarters_for_date_with_start(meeting.start, start_arrow)
            end_quarters = get_quarters_for_date_with_start(meeting.end, start_arrow)
            if end_quarters >= start_quarters:
                if start_quarters == end_quarters:
                    # just decrease start_quarters by 1 (the meeting date is
                    # something like 7:10 to 7:13)
                    start_quarters -= 1
                    if start_quarters == 0:
                        engine_meetings.append([0,1])
                    else:
                        engine_meetings.append([start_quarters, end_quarters])
                else:
                    engine_meetings.append([start_quarters, end_quarters])

    return engine_meetings



def interval_to_from_and_to(interval, start_arrow):
    """
    Transform an interval [x y] to a [from_arrow_date to_arrow_date]
    For example, 0 is start_arrow, 3 is 3 quarters after start_arrow
    """
    s = interval[0]
    e = interval[1]
    s_minutes = s*15
    e_minutes = e*15
    start = start_arrow.replace(minutes=+s_minutes)
    end = start_arrow.replace(minutes=+e_minutes)
    return [start, end]


def save_scheduleditems_from_engine(user, engine_items, engine_tasks, start_arrow):
    """
    Write scheduled items from the engine as ScheduleItems
    This is how scheduled items look:
        {'123': [[0, 3], [4, 5]]}
    """
    for task_id, schedule_items in engine_items.items():
        actual_duration = e.get_available_time(schedule_items)
        if task_id in engine_tasks and "duration" in engine_tasks[task_id] and actual_duration < engine_tasks[task_id]["duration"]:
            status = 1
        else:
            status = 0


        for item in schedule_items:
            if task_id in engine_tasks and "due" in engine_tasks[task_id] and item[0] >= engine_tasks[task_id]["due"]:
                status = 2
            
            from_to = interval_to_from_and_to(item, start_arrow)
            sch = ScheduleItem.objects.create(user=user, task=Task.objects.get(id=task_id), from_date=from_to[0].datetime, to_date=from_to[1].datetime)
            sch.status = status
            sch.save()

def clear_scheduleditems(user):
    """
    Deletes all ScheduledItems.
    """
    ScheduleItem.objects.filter(user=user).delete()

def clear_externalitems(user):
    """
    Deletes all foreign (google) items
    """
    Meeting.objects.filter(user=user, foreign=0).delete()



def get_arrow_datetime(weekday, t, start_arrow, user_timezone, workweek_done):
    """
    t is a datetime.time instance, weekday is 0..6 (0  is Monday)
    start_arrow is an arrow datetime object in UTC (usually indicating 'now')
    Note that day_string will be in reference to the user's timezone unfortunately. We are picking that timezone up from when the user presses the refresh schedule button.
    user_timezone is something like Americas/Los_Angeles
    workweek_done is a boolean indicating whether we should plan this week or the next
    """
    local_start_arrow = start_arrow.to(user_timezone)
    weekday_now = local_start_arrow.weekday()
    diff_days = weekday_now - weekday
    # same time as local_start_arrow but on weekday
    if not workweek_done:
        local_start_arrow_on_weekday = local_start_arrow.replace(days=-diff_days)
    else:
        # work week is done and we actually mean the next ones (so
        # +7)
        local_start_arrow_on_weekday = local_start_arrow.replace(days=+(7-diff_days))
    result = local_start_arrow_on_weekday.replace(hour=t.hour, minute=t.minute, second=t.second)
    return result

def work_week_over(start_arrow, preferences, user_timezone):
    if not preferences:
        return False
    else:
        largest_pref = preferences[0]

    local_start_arrow = start_arrow.to(user_timezone)
    weekday_now = local_start_arrow.weekday()

    # Set the largest pref
    # start from the rest of preferences
    for pref in preferences[1:]:
        if pref.day > largest_pref.day:
            largest_pref = pref
        elif pref.day == largest_pref.day:
            if pref.to_time > largest_pref.to_time:
                largest_pref = pref

    # Now compare the times on the local_start_arrow with the largest_pref
    if weekday_now > largest_pref.day:
        return True
    elif weekday_now == largest_pref.day:
        if local_start_arrow.hour > largest_pref.to_time.hour:
            return True
        elif local_start_arrow.hour == largest_pref.to_time.hour:
            if local_start_arrow.minute >= largest_pref.to_time.minute:
                return True
    return False
        
def preferences_to_engine(user, start_arrow, engine_meetings, user_timezone):
    """
    Write the UI preferences to preferences the engine can handle.
    Now it is for every preference begin-end, we create a internval [begin-quarter end-quarter].
    """
    preferences = Preference.objects.filter(user=user)
    result = { "today" : [], "thisweek" : [] }
    # is the work week over? (depending on it we calculate this week or next
    # week)
    workweek_done = work_week_over(start_arrow, preferences, user_timezone)
    start_user_timezone = start_arrow.to(user_timezone)
    for pref in preferences:
        actual_day_from = get_arrow_datetime(pref.day, pref.from_time, start_arrow, user_timezone, workweek_done)
        actual_day_to = get_arrow_datetime(pref.day, pref.to_time, start_arrow, user_timezone, workweek_done)
        quarters_from = get_quarters_for_date_with_start(actual_day_from.datetime, start_arrow)
        quarters_to = get_quarters_for_date_with_start(actual_day_to.datetime, start_arrow)
        # normalize:
        if quarters_to > 0:
            if quarters_from < 0:
                quarters_from = 0
            if actual_day_to.date() == start_user_timezone.date():
                # this means today (does this imply that start_arrow is always
                # supposed to be "now"?
                result["today"].append([quarters_from, quarters_to])
            else:
                result["thisweek"].append([quarters_from, quarters_to])

    # sort the intervals on the first item
#    result["today"].sort(key=lambda interval: interval[0])
#    result["thisweek"].sort(key=lambda interval: interval[0])  
    # the below also sorts them
    result = e.constrain_preferences_with_meetings(result, engine_meetings)
    return (result, workweek_done)

def nearest_quarter_time(start_arrow):
    """
    Find first following quarter in future.
    """
    mins = start_arrow.minute
    add = 0
    
    if 0 < mins < 15:
        add = 15-mins
    elif 15 < mins < 30:
        add = 30-mins
    elif 30 < mins < 45:
        add = 45-mins
    elif 45 < mins < 60:
        add = 60-mins

    return start_arrow.replace(minutes=+add, second=0, microsecond=0)

def schedule(user, user_timezone):
    """
    Schedule the whole lot.
    """
    error = ""
    warning = ""
    success = ""
    now = arrow.utcnow()
    now = nearest_quarter_time(now)
    tasks = get_tasks_to_schedule(user, now, user_timezone)
    if not tasks:
        warning = "No tasks were found for scheduling: did you indicate some tasks as Today or This Week?"
        return (error, warning, success)
        
    engine_tasks = tasks_to_engine(tasks, now)
    meetings = get_meetings_to_schedule(user, now, user_timezone)
    engine_meetings = meetings_to_engine(meetings, now)
    # give the meetings to the preferences
    preferences, workweek_done = preferences_to_engine(user, now, engine_meetings, user_timezone)
    if not preferences["today"] and not preferences["thisweek"]:
        warning = "There is no place to schedule your tasks. (Did you add Preferences? Given your meetings, is there still space this week to schedule any tasks?)"
        return (error, warning, success)
    schedule = e.plan(engine_tasks, preferences)
    if schedule:
        clear_scheduleditems(user)
        save_scheduleditems_from_engine(user, schedule, engine_tasks, now)
        if workweek_done:
            return ("", "", "Next Week's Schedule Calculated.")
        else:
            return ("", "", "Schedule Calculated.")
    else:
        error = "The engine was not able to schedule your tasks."
        error_message_for_debug = "no sched: tsks = %s, mtngs = %s, and prefs = %s for user %s" % (engine_tasks, engine_meetings, preferences, user)
        logger.error(error_message_for_debug)
        return (error, warning, success)

def get_timezone(user):
    profile = user.userprofile
    return profile.timezone.zone

def create_default_preferences(user):
    """
    Set up default preferences for a user.
    """
    p1 = Preference.objects.create(user=user, day=0, from_time="09:00", to_time="17:00")
    p2 = Preference.objects.create(user=user, day=1, from_time="09:00", to_time="17:00")
    p3 = Preference.objects.create(user=user, day=2, from_time="09:00", to_time="17:00")
    p4 = Preference.objects.create(user=user, day=3, from_time="09:00", to_time="17:00")
    p5 = Preference.objects.create(user=user, day=4, from_time="09:00", to_time="17:00")
    p1.save()
    p2.save()
    p3.save()
    p4.save()
    p5.save()


def get_current_and_next_up_in_schedule(user):
    meetings = get_future_meetings(user).order_by('start')
    # we use iterators to avoid evaluating the filter by getting all meetings
    # for the user http://blog.etianen.com/blog/2013/06/08/django-querysets/
    # TODO should we apply that technique also elsewhere
    meetings_iterator = meetings.iterator()
    
    first_meeting = None
    second_meeting = None
    try:
        first_meeting = next(meetings_iterator)
        try:
            second_meeting = next(meetings_iterator)
        except StopIteration:
            pass
    except StopIteration:
        pass

    scheduleitems = get_future_scheduleitems(user).order_by('from_date')
    items_iterator = scheduleitems.iterator()
    first_item = None
    second_item = None
    try:
        first_item = next(items_iterator)
        try:
            second_item = next(items_iterator)
        except StopIteration:
            pass
    except StopIteration:
        pass

    result = [first_meeting, second_meeting, first_item, second_item]
    # Get rid of the None
    result = [ i for i in result if i is not None ]
    result.sort(key=lambda(i): i.from_date if isinstance(i, ScheduleItem) else i.start if isinstance(i, Meeting) else i)
    return result[0:2]


def beta_registrations_left():
    result = 0
    if parameters.TOTAL_ALLOWED_BETA_USERS:
        # do not count admin account (+ 1)
        result = parameters.TOTAL_ALLOWED_BETA_USERS - UserProfile.objects.filter(usertype=0).count() + 1

    if result < 0:
        return 0
    else:
        return result
    
    
def trial_registrations_left():
    # note that we DO NOT do an evaluate_trial on each user, that's expensive
    # We do check for (1) are you a trial user and (2) when have you joined. If
    # you joined longer than 32 days ago, and are still a trial user, that just
    # means you never were put to undecided by the application cause you never
    # did anything useful anymore in the application. So you do not count
    # toward the trial count.
    result = 0
    if parameters.TOTAL_ALLOWED_TRIAL_USERS:
        definitely_stale_date = arrow.utcnow().replace(days=-32).datetime
        joined_recently = Q(user__date_joined__gt=definitely_stale_date)
        trial_users = UserProfile.objects.filter(joined_recently, usertype=1)
            
        result = parameters.TOTAL_ALLOWED_TRIAL_USERS - trial_users.count()

    if result < 0:
        return 0
    else:
        return result

def free_registrations_left():
    free_users = UserProfile.objects.filter(usertype=6)
    return parameters.TOTAL_ALLOWED_FREE_USERS - free_users.count()
            
## Google

# Save Google Calendar Events to our Meetings
def save_google_events(user, events, calendar_name):
    user_timezone = get_timezone(user)
    # rewrite calendar_name for unicode
    calendar_name = smart_str(calendar_name)

    error = ""
    warning = ""
    success = ""

    for event in events['items']:
        s = event['start']
        e = event['end']

        if 'summary' in event and event['summary'] is not None:
            summary = smart_str(event['summary'])
        else:
            summary = "(No title)"

        if 'date' in s:
            # Do not take all-day events into account
            continue
        if 'date' in e:
            # Do not take all-day events into account
            continue

        if 'dateTime' in s:
            start = arrow.get(s['dateTime'])
        if 'dateTime' in e:
            end = arrow.get(e['dateTime'])

        if 'timeZone' in s:
            start = start.to(s['timeZone'])
        if 'timeZone' in e:
            end = end.to(e['timeZone'])

        if start and end:
            meeting = Meeting.objects.create(user=user, name=smart_str(summary) + " (" + str(calendar_name) + ")", start=start.datetime, end=end.datetime, foreign=0)
            meeting.save()
            
    success = calendar_name + ": Imported this week's items for scheduling."
    return (error, warning, success)


## Creating tasks out of habits

def spawn_tasks(user, user_timezone, when):
    """
    Create tasks out of schedule.
    """
    error = ""
    warning = ""
    success = ""

    habits = Habit.objects.filter(user=user, when=when)
    if not habits:
        if when == 'T':
            warning = "You do not have any daily Habits currently. No tasks for today created."
        elif when == 'W':
            warning = "You do not have any weekly Habits currently. No tasks for this week created."
        return (error, warning, success)
    else:
        for habit in habits:
            if habit.when:
                task = Task.objects.create(user=user, name=habit.name, topic=habit.topic, when=habit.when, duration=habit.duration, note=habit.note, done=False, habit=True)
                task.save()
        if when == 'T':
            success = "Tasks created and moved to Today."
        elif when == 'W':
            success = "Tasks created and moved to This Week."

    return (error, warning, success)


