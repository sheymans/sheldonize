
"""
Assumptions:

    time goes from 0, 1, 2, 3, (each is 15 minutes interval)

Tasks: 
Assume "when" is always present. Other tasks do not get scheduled.

{ id1 : { "when": 0 or 1, "comes_after" : "id", due: integer, duration : integer }, id2 : {...} }

Preferences

{ today: [ [s1 e1] [s2 e2]], thisweek [[s1 e1] [s2 e2]] }

today: indicates what time intervals are available for scheduling today. thisweek: indicates what intervals are available for scheduling thisweek.

State (representing scheduleditems):

    A dictionary with keys task ids and values list of intervals:

        state1 = { "123" : [ [0, 1], [3, 5]], "345": [ [6, 9], [89, 90]] }

"""

import copy
import math
from timer import Timer
from sort import sort_tasks



def constrain_interval_with_interval(interval1, interval2):

    i1 = interval1[0]
    i2 = interval1[1]
    j1 = interval2[0]
    j2 = interval2[1]

    if j1 >= i2 or j2 <= i1:
        # then the second interval is just disjoint with this interval
        return [interval1]

    if i1 < j1:
        if j2 < i2:
            return [[i1, j1], [j2, i2]]
        else:
            return [[i1, j1]]
    else:
        if j2 < i2:
            return [[j2, i2]]
        else:
            return []

def constrain_intervals_with_interval(intervals, interval):
    result = []
    for i in intervals:
        result.extend(constrain_interval_with_interval(i, interval))
    return result

def constrain_preferences_with_meetings(preferences, meetings):
    today = preferences["today"]
    thisweek = preferences["thisweek"]

    constrained_today = list(today)
    constrained_thisweek = list(thisweek)
    for m in meetings:
        constrained_today = constrain_intervals_with_interval(constrained_today, m)
        constrained_thisweek = constrain_intervals_with_interval(constrained_thisweek, m)

    constrained_today.sort(key=lambda interval: interval[0])
    constrained_thisweek.sort(key=lambda interval: interval[0])
    return { "today": constrained_today, "thisweek": constrained_thisweek}


def get_tasks_divided_up(tasks):
    tasks_today = {}
    tasks_thisweek = {}
    for task_id, value in tasks.items():
        if "when" in value and value["when"] == 0:
            tasks_today[task_id] = value
        if "when" in value and value["when"] == 1:
            tasks_thisweek[task_id] = value
    return (tasks_today, tasks_thisweek)

def get_preferences_divided_up(preferences):
    if "today" in preferences and "thisweek" in preferences:
        return (preferences["today"], preferences["thisweek"])
    elif "today" in preferences:
        return (preferences["today"], [])
    elif "thisweek" in preferences:
        return([], preferences["thisweek"])
    else:
        return ([], [])


def time_in_interval(interval):
    return interval[1] - interval[0]

def get_available_time(intervals):
    total = 0
    for interval in intervals:
        total += time_in_interval(interval)
    return total

def get_tasks_with_duration(tasks):
    # in python 2.7 you could use dict comprehension directly
    return dict((task_id,task_value) for task_id, task_value in tasks.iteritems() if "duration" in task_value and task_value["duration"] >= 1)

def get_tasks_without_duration(tasks):
    return dict((task_id,task_value) for task_id, task_value in tasks.iteritems() if "duration" not in task_value or task_value["duration"] < 1)

def get_flex_total(tasks):
    flex = 0
    for task_id, task_value in tasks.items():
        if "flex" in task_value:
            flex += task_value["flex"]
    return flex

def assign_flexible_durations(tasks, available_time):
    """
    Assign the flex attribute of each task such that it is close to it's
    duration (maximized), greater than 1, and equal to the available time.  We
    know that assigning all tasks to 1 will be definitely smaller than the
    available time, because of how this is called.
    """
    # Initialize: this is always fine.
    for task_id, task_value in tasks.items():
        task_value["flex"] = 1

    if len(tasks) < available_time:
        # this means we can do better than just 1 on each task
        # We'll first cycle through the tasks with duration to try to optimize
        # their durations, one by one:
        tasks_with_duration_list = get_tasks_with_duration(tasks).keys()
        if (len(tasks_with_duration_list) > 0):
            current_flex_total = get_flex_total(tasks)
            current_index = 0
            while (current_flex_total < available_time and len(tasks_with_duration_list) > 0):
                # increase 1 task with duration with 1 (we cycle through them using
                # tasks_with_duration_list)
                current_task_index = tasks_with_duration_list[current_index]
                # max_flex is what we added to ensure due dates are being
                # satisfied
                if (tasks[current_task_index]["flex"] == tasks[current_task_index]["duration"] or ("max_flex" in tasks[current_task_index] and tasks[current_task_index]["flex"] == tasks[current_task_index]["max_flex"])):
                    # then we can no longer increase this flex, so we get rid
                    # of it from the list of things to consider
                    tasks_with_duration_list.pop(current_index)
                    # move through next one
                    if tasks_with_duration_list: # you cannot take module of the list is now null
                        current_index = (current_index + 1) % len(tasks_with_duration_list)
                else:
                    # we should try to increase this flex
                    tasks[current_task_index]["flex"] += 1
                    current_index = (current_index + 1) % len(tasks_with_duration_list)
                    current_flex_total += 1
        # Proceed with trying to increase all tasks without duration one by
        # one:
        tasks_without_duration_list = get_tasks_without_duration(tasks).keys()
        if (len(tasks_without_duration_list) > 0):
            current_flex_total = get_flex_total(tasks)
            current_index = 0
            while (current_flex_total < available_time and len(tasks_without_duration_list) > 0):
                current_task_index = tasks_without_duration_list[current_index]
                if "max_flex" in tasks[current_task_index] and tasks[current_task_index]["flex"] == tasks[current_task_index]["max_flex"]:
                    tasks_without_duration_list.pop(current_index)
                    if tasks_without_duration_list: # you cannot take module of the list is now null
                        current_index = (current_index + 1) % len(tasks_without_duration_list)
                else:
                    tasks[current_task_index]["flex"] += 1
                    current_index = (current_index + 1) % len(tasks_without_duration_list)
                    current_flex_total += 1


def put_one_task_on_schedule(task_id, task_value, schedule, preferences):
    """
    Put the task on the schedule given the preferences.
    """
    flex = task_value["flex"]
    #print "this is the flex of ", task_id, " : ", flex
    # make sure something to make place for the task in the schedule before
    # starting to append:
    if not task_id in schedule:
        schedule[task_id] = []
    if preferences:
        preference = preferences[0]
        #print "current preference: ", preference
        time_in_pref = time_in_interval(preference)
        #print "time in current preference: ", time_in_pref
        if flex <= time_in_pref:
            # it fits
            start = preference[0]
            end = start + flex
            schedule[task_id].append([start, end])
            # modify the preferences
            if flex == time_in_pref:
                # remove the preference then (no place anymore for any other
                # task)
                preferences.pop(0)
            else:
                # remains of the preference after you removed task from it
                preferences[0] = [end, preference[1]]
            
            return (schedule, preferences)
                
        else:
            # take up the whole preference and continue
            schedule[task_id].append(preference)
            # remove the preference
            preferences.pop(0)
            # the flex is now shorter, but since flex > time_in_pref it will be
            # at least 1
            task_value["flex"] = flex - time_in_pref
            # and recurse
            return put_one_task_on_schedule(task_id, task_value, schedule, preferences)
    return (schedule, preferences)


def max_intervals(intervals):
    m = 0
    for i in intervals:
        if i[1] > m:
            m = i[1]
    return m

def last_interval(intervals):
    l = len(intervals)
    return intervals[l-1]


def can_still_reduce(schedule_items):
    return len(schedule_items) > 1 or time_in_interval(schedule_items[0]) > 1

def done_trying_to_update_schedule_for_due_dates(tasks, schedule):
    #print "testing whether schedule is done for tasks: ", tasks
    for task_id, schedule_items in schedule.iteritems():
        m = max_intervals(schedule_items)
        if "due" in tasks[task_id]:
            due = tasks[task_id]["due"]
            if m > due and can_still_reduce(schedule_items):
                return False
    return True
        
def assign_max_durations(tasks, sorted_task_ids, preferences, schedule):
    # we want to try to reduce one max duration (NOT necessarily just of the
    # violating task -- we try also to put max flexes on the tasks before the
    # violating tasks. We do that by selecting from:
    # (1) the tasks that come before the violating task (violating = due not
    # satisfied) or that violating task itself
    # (2) from those tasks pick a task that has max_flex not yet set or which
    # has the maximum max_flex
    
    # candidates: all tasks before a task that is a violated + the task itself,
    # but without the tasks where the max_flex is already 1 (you cannot reduce
    # those anymore)
    candidate_tasks = []
    found_a_violation = False
    for task_id in sorted_task_ids:
        if "due" not in tasks[task_id]:
            candidate_tasks.append(task_id)
            continue
        if "max_flex" in tasks[task_id] and tasks[task_id]["max_flex"] <= 1:
            # do not pick this one, already minimized
            continue
        schedule_items = schedule[task_id]
        if not can_still_reduce(schedule_items):
            continue
        m = max_intervals(schedule_items)
        due = tasks[task_id]["due"]
        # not violating
        if m <= due:
            candidate_tasks.append(task_id)
            continue
        if m > due:
            # this is a violator!
            # we add it and stop the loop
            candidate_tasks.append(task_id)
            found_a_violation = True
            break

    if found_a_violation:
        # pick the task with the max flex (to equalize them) TODO: maybe also
        # consider max_flex or duration?
        task_id = max(candidate_tasks, key=lambda t_id: tasks[t_id]["flex"] if "flex" in tasks[t_id] else 0)
        task = tasks[task_id]
        task["max_flex"] = task["flex"] - 1

def put_tasks_on_schedule(tasks, sorted_task_ids, preferences, schedule, available_time):

    # make a copy of the preferences, we want to keep the original preferences
    accu_prefs = list(preferences)

    if sorted_task_ids: # if you managed to sort
        # add the flex 
        assign_flexible_durations(tasks, available_time)
        for task_id in sorted_task_ids:
            task_value = tasks[task_id]
            (new_schedule, new_preferences) = put_one_task_on_schedule(task_id, task_value, schedule, accu_prefs)
            #print "new_schedule ", new_schedule
            #print "new_preferences ", new_preferences
            # update 
            schedule = new_schedule
            accu_prefs = new_preferences
        
        # now vefify the due dates before return the schedule. If due dates not
        # satisfied calculate again with max_flexes.
        if done_trying_to_update_schedule_for_due_dates(tasks, schedule):
            return schedule
        else:
            # you want to set the initial flexible durations (the max durations
            # depend on these original values for reducing those)
            assign_flexible_durations(tasks, available_time)
            assign_max_durations(tasks, sorted_task_ids, preferences, schedule)
            # reset the schedule after that (we recalculate!)
            schedule = {}
            return put_tasks_on_schedule(tasks, sorted_task_ids, preferences, schedule, available_time)
    else:
        return {}


def go_plan(tasks, preferences):
    
    # this is the available time the preferences have:
    available_time = get_available_time(preferences)
    #print "available time ", available_time

    # if you don't have this minimum available you cannot schedule
    minimum_time_needed =  len(tasks)
    #print "minimul time needed ", minimum_time_needed

    if minimum_time_needed <= available_time:
        result_schedule = {}
        # we sort the tasks according to comes_after and due:
        sorted_task_ids = sort_tasks(tasks)
        if sorted_task_ids:
            return put_tasks_on_schedule(tasks, sorted_task_ids, preferences, result_schedule, available_time)
        else:
            return {}
    else:
        return {}

def plan(tasks, preferences):

    (tasks_today , tasks_thisweek) = get_tasks_divided_up(tasks)


    #print "tasks today ", tasks_today
    (preferences_today , preferences_thisweek) = get_preferences_divided_up(preferences)
    #print "preferences today ", preferences_today
    
    schedule_today = go_plan(tasks_today, preferences_today)
    #print "schedule today ", schedule_today
    schedule_thisweek = go_plan(tasks_thisweek, preferences_thisweek)


    # merge the found schedules
    schedule = schedule_today.copy()
    schedule.update(schedule_thisweek)

    return schedule

