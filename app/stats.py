from models import Task, ScheduleItem, Preference, Meeting
import arrow


def collect_weekly_todos(user):
    done_tasks = Task.objects.filter(user=user, done=True)
    if done_tasks:
        first_done_date = done_tasks[0].done_date
        first_task_iso = arrow.get(first_done_date).isocalendar()
        last_task_iso = first_task_iso
        year_weeknumber_data = {}
        for t in done_tasks:
            if t.done_date:
                iso = arrow.get(t.done_date).isocalendar()
                print "iso: ", iso
                if iso < first_task_iso:
                    first_task_iso = iso
                if iso > last_task_iso:
                    last_task_iso = iso

                # now add it to our dict of (year, weeknumbers):
                if (iso[0], iso[1]) in year_weeknumber_data:
                    year_weeknumber_data[(iso[0], iso[1])] += 1
                else:
                    year_weeknumber_data[(iso[0], iso[1])] = 1

        max_todos_done = 1
        for key, value in year_weeknumber_data.iteritems():
            if value > max_todos_done:
                max_todos_done = value

        return (first_task_iso, last_task_iso, max_todos_done, year_weeknumber_data)
    else:
        return None


