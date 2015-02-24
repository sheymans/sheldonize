from django.contrib import admin

from app.models import Task, ScheduleItem, Meeting, Preference, CredentialsModel, FlowModel, Habit, Project

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'done', 'done_date', 'due', 'comes_after', 'topic', 'when', 'duration', 'created', 'user', 'habit')

class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'when', 'duration', 'created', 'user')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_of')

class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('task', 'from_date', 'to_date', 'status', 'user')

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'user', 'repeat', 'foreign')

class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('day', 'from_time', 'to_time', 'user')


# Google
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'credential' )

class FlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'flow' )

class StorageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Task, TaskAdmin)
admin.site.register(Habit, HabitAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Preference, PreferenceAdmin)
admin.site.register(CredentialsModel, CredentialsAdmin)
admin.site.register(FlowModel, FlowAdmin)
