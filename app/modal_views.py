# We write our modal views here (Meetings, Tasks, etc)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from models import Meeting, Task
from forms import MeetingForm, TaskForm
from braces.views import LoginRequiredMixin

# from django-fm
from fm.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView

class MeetingUpdateView(AjaxUpdateView, LoginRequiredMixin):
    form_class = MeetingForm
    model = Meeting
    pk_url_kwarg = 'meeting_pk'

    def post_save(self):
        messages.add_message(self.request, messages.SUCCESS, "Updated meeting.")
        pass

    def pre_save(self):
        # before saving we need to make sure that the note and foreign states
        # are propertly set again (the form upon submission does not have
        # those)
        # self.object is at this point the form (see form_valid in
        # AjaxUpdateView)
        
        # we pick up the original out of the database:
        meeting = get_object_or_404(Meeting, pk=self.object.id)
        foreign_marker = meeting.foreign
        original_note = Meeting.objects.get(id=meeting.id).note
        
        # now set those values in self.object (which is the object that is
        # going to be saved):
        self.object.foreign = foreign_marker
        self.object.note = original_note
        pass

class MeetingDeleteView(AjaxDeleteView, LoginRequiredMixin):
    model = Meeting
    pk_url_kwarg = 'meeting_pk'

    def post_delete(self):
        messages.add_message(self.request, messages.SUCCESS, "Deleted meeting.")
        pass

class TaskUpdateView(AjaxUpdateView, LoginRequiredMixin):
    # the default is app/modal_form which is for meetings.
    template_name = "app/modal_form_task.html"
    form_class = TaskForm
    model = Task
    pk_url_kwarg = 'task_pk'

    def post_save(self):
        messages.add_message(self.request, messages.SUCCESS, "Updated Task.")
        pass

    def pre_save(self):
        # before saving we need to make sure that the note and foreign states
        # are propertly set again (the form upon submission does not have
        # those)
        # self.object is at this point the form (see form_valid in
        # AjaxUpdateView)
        
        # we pick up the original out of the database:
        task = get_object_or_404(Task, pk=self.object.id)
        original_note = Task.objects.get(id=task.id).note
        
        # now set those values in self.object (which is the object that is
        # going to be saved):
        self.object.note = original_note
        pass

class TaskDeleteView(AjaxDeleteView, LoginRequiredMixin):
    template_name = "app/modal_form_task.html"
    model = Task
    pk_url_kwarg = 'task_pk'

    def post_delete(self):
        messages.add_message(self.request, messages.SUCCESS, "Deleted task.")
        pass


