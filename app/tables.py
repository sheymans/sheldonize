import django_tables2 as tables
import arrow

from django_tables2.utils import A
from django_tables2.utils import OrderByTuple, OrderBy, Accessor
from models import Task, Preference, Meeting, ScheduleItem, Habit
# to not escape html
from django.utils.safestring import mark_safe


## Overriding the table sorting.
## NOTE: in the current (2014078 version) and the original order_by in tables.py of django_tables2 hasattr(self, "queryset") is always true it seems;
## so we did not modify OrderTuple's function (called "key") for sorting. consider that if we would find out that also self.list.sort
## gets called.
## This is a rewrite of the order_by function in TableData at: https://github.com/bradleyayers/django-tables2/blob/master/django_tables2/tables.py
def order_by(self, aliases):
    accessors = []
    for alias in aliases:
        bound_column = self.table.columns[OrderBy(alias).bare]
        if alias[0] != bound_column.order_by_alias[0]:
            accessors += bound_column.order_by.opposite
        else:
            accessors += bound_column.order_by
    if hasattr(self, "queryset"):
    
        translate = lambda accessor: accessor.replace(Accessor.SEPARATOR, tables.tables.QUERYSET_ACCESSOR_SEPARATOR)
        # OLD statement
        #self.queryset = self.queryset.order_by(*(translate(a) for a in accessors))
        # new statement: we add extra SQL (this is raw SQL!!!!!!!) but is
        # really the only way to properly but None at the back:
        # http://stackoverflow.com/questions/11769805/django-ordering-query-set-in-ascending-order
        # Further note that NOW() depends on the MySQL settings on the server
        # (which is UTC in our case, but local on local machine, where I
        # edited /etc/mysql/my.. to set the default-timezone)
        if self.queryset.count() > 0 and isinstance(self.queryset[0], Task):
#            self.queryset = self.queryset.extra(select={'just_added': 'DATE_ADD(app_task.created, INTERVAL 1 MINUTE) >= NOW()', 'null_when': 'app_task.when is null', 'null_due': 'app_task.due is null','null_topic': 'length(app_task.topic) <= 0' }).order_by('-just_added', 'null_when', 'when', 'null_due', 'due', 'null_topic', 'topic', '-created')
            if 'topic' in accessors:
                self.queryset = self.queryset.extra(select={'null_topic': 'length(app_task.topic) <= 0' }).order_by('null_topic', *(translate(a) for a in accessors))
            elif 'when' in accessors:
                self.queryset = self.queryset.extra(select={'null_when': 'app_task.when is null'}).order_by('null_when', *(translate(a) for a in accessors))
            elif 'priority' in accessors:
                self.queryset = self.queryset.extra(select={'null_priority': 'app_task.priority is null'}).order_by('null_priority', *(translate(a) for a in accessors))
            elif 'due' in accessors:
                self.queryset = self.queryset.extra(select={'null_due': 'app_task.due is null'}).order_by('null_due', *(translate(a) for a in accessors))
            elif 'comes_after' in accessors:
                self.queryset = self.queryset.extra(select={'null_comes_after': 'app_task.comes_after_id is null'}).order_by('null_comes_after', *(translate(a) for a in accessors))
            elif 'duration' in accessors:
                self.queryset = self.queryset.extra(select={'null_duration': 'app_task.duration is null'}).order_by('null_duration', *(translate(a) for a in accessors))
            else:
                self.queryset = self.queryset.order_by(*(translate(a) for a in accessors))
        elif self.queryset.count() > 0 and isinstance(self.queryset[0], Habit):
            if 'topic' in accessors:
                self.queryset = self.queryset.extra(select={'null_topic': 'length(app_habit.topic) <= 0' }).order_by('null_topic', *(translate(a) for a in accessors))
            elif 'when' in accessors:
                self.queryset = self.queryset.extra(select={'null_when': 'app_habit.when is null'}).order_by('null_when', *(translate(a) for a in accessors))
            elif 'duration' in accessors:
                self.queryset = self.queryset.extra(select={'null_duration': 'app_habit.duration is null'}).order_by('null_duration', *(translate(a) for a in accessors))
            else:
                self.queryset = self.queryset.order_by(*(translate(a) for a in accessors))
 
        else:
            self.queryset = self.queryset.order_by(*(translate(a) for a in accessors))
    else:
        # Normally never called it seems (if it is sorting will be normal < )
        self.list.sort(key=OrderByTuple(accessors).key)

## Setting the new order by function
tables.tables.TableData.order_by = order_by

class TaskTable(tables.Table):
    
    selection = tables.CheckBoxColumn(accessor="pk", attrs = { "th__input": {"onclick": "toggle(this)"}}, orderable=False)
    #edit = tables.TemplateColumn('<a class="table_edit" href="{{ record.id }}"><span class="glyphicon glyphicon-edit"</span></a>')
    topic = tables.Column(empty_values=())
    when = tables.Column(empty_values=())
    priority = tables.Column(empty_values=())
    duration = tables.Column(empty_values=())
    comes_after = tables.Column(empty_values=())
    # the habit indication
    habit = tables.TemplateColumn('{% if record.habit %}<span class="glyphicon glyphicon-repeat"</span>{% endif %}')

    def render_created(self, value, record):
        # value is utc record.timezone is something like America/Los_Angeles
        timezone = record.user.userprofile.timezone.zone
        if timezone:
            local_display = arrow.get(value).to(timezone)
        else:
            local_display = arrow.get(value)
        return local_display.humanize()

    def render_name(self, value, record):
        if value:
            shorter = (value[:65] + '..') if len(value) > 65 else value
            return shorter
        else:
            return ""

    def render_due(self, value, record):
        # value is utc record.timezone is something like America/Los_Angeles
        timezone = record.user.userprofile.timezone.zone
        if timezone and value:
            local_display = arrow.get(value).to(timezone)
            return local_display.humanize()
        else:
            return ""

    def render_topic(self, value, record):
        if value:
            return "(" + value + ")"
        else:
            return ""

    def render_when(self, value, record):
        if value:
            return value
        else:
            return ""

    def render_priority(self, value, record):
        if value:
            return value
        else:
            return ""

    def render_duration(self, value, record):
        if value:
            return str(value) + " mins"
        else:
            return ""

    def render_comes_after(self, value, record):
        if value:
            # value is of type Task (the comes_after)
            shorter = (value.name[:15] + '..') if len(value.name) > 15 else value.name
            return mark_safe("<i>" + shorter + "</i>")
        else:
            return ""

    class Meta:
        model = Task
        fields = ('selection', 'name', 'priority', 'topic', 'due', 'when', 'duration', 'comes_after', 'created')
        sequence = ('selection', 'name', 'priority', 'topic', 'duration',  'comes_after', 'due',  'created')
        exclude = ('done', 'when', 'user', )
        # default ordering
        # we removed the ordering for Tasks as we are doing it via the raw SQL
        # see redefinition of order_by
        order_by = ('-created')
        attrs = {"class": "table table-hover"}


class HabitTable(tables.Table):
    
    selection = tables.CheckBoxColumn(accessor="pk", attrs = { "th__input": {"onclick": "toggle(this)"}}, orderable=False)
    topic = tables.Column(empty_values=())
    when = tables.Column(empty_values=())
    duration = tables.Column(empty_values=())

    def render_created(self, value, record):
        # value is utc record.timezone is something like America/Los_Angeles
        timezone = record.user.userprofile.timezone.zone
        if timezone:
            local_display = arrow.get(value).to(timezone)
        else:
            local_display = arrow.get(value)
        return local_display.humanize()

    def render_name(self, value, record):
        if value:
            shorter = (value[:65] + '..') if len(value) > 65 else value
            return shorter
        else:
            return ""

    def render_topic(self, value, record):
        if value:
            return "(" + value + ")"
        else:
            return ""

    def render_when(self, value, record):
        if value:
            return value
        else:
            return ""

    def render_duration(self, value, record):
        if value:
            return str(value) + " mins"
        else:
            return ""

    class Meta:
        model = Habit 
        fields = ('selection', 'name', 'topic', 'when', 'duration', 'created')
        sequence = ('selection', 'name', 'topic', 'when', 'duration', 'created')
        exclude = ('done', 'user', )
        # default ordering
        order_by = ('-created')
        attrs = {"class": "table table-hover"}




class MeetingTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor="pk", attrs = { "th__input": 
        {"onclick": "toggle(this)"}}, orderable=False)
    #edit = tables.TemplateColumn('<a class="table_edit" href="{{ record.id }}"><span class="glyphicon glyphicon-edit"</span></a>')


    def render_start(self, value, record):
        # value is utc, record.timezone is something like America/Los_Angeles
        timezone = record.user.userprofile.timezone.zone
        if timezone:
            local_display = arrow.get(value).to(timezone)
        else:
            local_display = arrow.get(value)

        return local_display.format("DD MMM hh:mm a")

    def render_end(self, value, record):
        # value is utc, record.timezone is something like America/Los_Angeles
        timezone = record.user.userprofile.timezone.zone
        if timezone:
            local_display = arrow.get(value).to(timezone)
        else:
            local_display = arrow.get(value)
        return local_display.format("DD MMM hh:mm a")

    def render_repeat(self, value, record):
        if value:
            return value
        else:
            return ""

    def render_external(self, value, record):
        if value:
            return value
        else:
            return ""



    class Meta:
        model = Meeting
        fields = ('selection', 'name', 'start', 'end', 'repeat', 'foreign')
        sequence = ('selection', 'name', 'start', 'end', 'repeat', 'foreign')
        exclude = ('user',)
        order_by = ('start')
        attrs = {"class": "table table-hover"}



class PreferenceTable(tables.Table):
    delete = tables.TemplateColumn('<a class="table_trash" href="{{ record.id }}"><span class="glyphicon glyphicon-trash"</span></a>')
    class Meta:
        model = Preference
        order_by = ('day', 'from_time')
        attrs = {"class": "table table-hover"}
        fields = ('day', 'from_time', 'to_time')
        exclude = ('user')
