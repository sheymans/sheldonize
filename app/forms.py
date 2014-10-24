from django import forms
from django.forms import ModelForm, DateTimeField, TimeField, CharField, HiddenInput, DateField
from django.core.urlresolvers import reverse
from models import Task, Preference, Meeting

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, BaseInput 
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, Div, PrependedText

# for redefining submitbutton, see
# https://github.com/maraujop/django-crispy-forms/issues/242
from django.conf import settings

import arrow

###############################################################################################
# https://github.com/maraujop/django-crispy-forms/issues/242
TEMPLATE_PACK = getattr(settings, 'CRISPY_TEMPLATE_PACK', 'bootstrap')
class SubmitButton(BaseInput):
    input_type = 'submit'
    field_classes = 'button' if TEMPLATE_PACK == 'uni_form' else 'btn' #removed btn-primary

################################################################################################


class TaskForm(ModelForm):
    # From moment.js to django input formats; translation is in the code here:
    # https://github.com/nkunihiko/django-bootstrap3-datetimepicker/blob/master/bootstrap3_datetime/widgets.py
    due = DateTimeField(required=False,input_formats = ['%m/%d/%Y %I:%M %p'])
    helper = FormHelper()
    helper.form_class='form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.form_method = 'POST'
    # the action is what we need to catch
    helper.form_action = '.'
    helper.add_input(SubmitButton('submit_save_task', 'Update', css_class='btn-sheldonize btn-sheldonize-primary'))
    helper.add_input(SubmitButton('delete-task', 'Delete', css_class='btn-sheldonize btn-sheldonize-default details-delete-button'))

    helper.layout = Layout(
            # Prepended text for boolean field to trick it
            # (http://stackoverflow.com/questions/22002861/booleanfield-checkbox-not-render-correctly-with-crispy-forms-using-bootstrap)
            PrependedText('done', ''),
            #Field('done'),
            Field('name', placeholder='a name for your task (make it actionable)'),
            Field('priority'),
            Field('due', placeholder='the date and time this task is due, leave empty if no due date'),
            Field('topic', placeholder='general area/topic/project this task belongs to'),
            Field('when'), 
            Field('duration', placeholder='how long do you think your task will at most take (in minutes)'),
            Field('comes_after'),
            )   

    def __init__(self, *args, **kwargs):
        # we need to call super before we call initial as we need the
        # self.instance, which we don't have access to otherwise later.
        super(TaskForm, self).__init__(*args, **kwargs)
        # if there is a due date on the Task instance you use to create this
        # task
        if self.instance.due:
            # get that date and put it in the right timezone
            # we need .zone as this is a pytz timezone object (from
            # timezone_field)
            timezone = self.instance.user.userprofile.timezone.zone
            new_date_arrow = arrow.get(self.instance.due).to(timezone)
            initial = kwargs.get('initial', {})
            # Back from the django format to Arrow format:
            initial['due'] = new_date_arrow.format("MM/DD/YYYY h:mm a")
            kwargs['initial'] = initial

        super(TaskForm, self).__init__(*args, **kwargs)
        # you need to exclude the id itself from the possible values. Note that
        # we can only use this self.fields AFTER having called super. The
        # initial stuff needs to be done before as it sets the initial VALUES
        # (you could set the default comes after task there for example).
        self.fields['comes_after'].queryset = Task.objects.filter(user=self.instance.user).exclude(id__exact=self.instance.id).exclude(done=True)


    def clean_due(self):
        # this gets called before saving
        # make sure when saving the form again saves in the right timezone
        # (bootstrap timepicker always just returns +00:00)
        form_due = self.cleaned_data['due']
        if form_due:
            timezone = self.instance.user.userprofile.timezone.zone
            new_arrow = arrow.get(form_due).replace(tzinfo=timezone)
            self.cleaned_data['due'] = new_arrow.datetime
        return self.cleaned_data['due']
 
                            
    class Meta:
        model = Task
        exclude = ('user',)

class AddTaskForm(ModelForm):


    helper = FormHelper()
    helper.form_class = 'form-horizontal sheldonize-form'
    helper.field_class = 'col-xs-12'
    helper.form_method = 'POST'
    helper.form_action = '.'

    helper.layout = Layout(
            FieldWithButtons(
                Field('name', placeholder="Quick add tasks (press Enter or the '+' sign)"),
                StrictButton('<span class="glyphicon glyphicon-plus"></span>', type="submit", name="new_task", css_class='btn btn-sheldonize btn-sheldonize-default'))
      )
    class Meta:
        model = Task
        exclude = ('user',)


class AddPreferenceForm(ModelForm):
    from_time = DateTimeField(required=False,input_formats = ['%I:%M %p'])
    to_time = DateTimeField(required=False,input_formats = ['%I:%M %p'])

    helper = FormHelper()
    helper.form_class = 'form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    #helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.form_method = 'POST'
    helper.form_action = '.'
    helper.add_input(SubmitButton('new_preference', 'Add', css_class='btn-sheldonize btn-sheldonize-primary preference-add-button'))

    helper.layout = Layout(
                Field('day', placeholder="a day to work"),
                Field('from_time', placeholder="start work day"),
                Field('to_time', placeholder="end work day"),
#                StrictButton("Add Preference", type="submit", name="new_preference", css_class='btn btn-sheldonize btn-sheldonize-default')
            )
    class Meta:
        model = Preference
        exclude = ('user',)


### Meeting forms

class MeetingForm(ModelForm):
    start = DateTimeField(required=False,input_formats = ['%m/%d/%Y %I:%M %p'])
    end = DateTimeField(required=False,input_formats = ['%m/%d/%Y %I:%M %p'])

    helper = FormHelper()
    helper.form_class='form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.form_method = 'POST'
    # the action is what we need to catch
    helper.form_action = '.'
    helper.add_input(SubmitButton('submit_save_meeting', 'Update', css_class='btn btn-sheldonize btn-sheldonize-primary'))
    helper.add_input(SubmitButton('delete-meeting', 'Delete', css_class='btn btn-sheldonize btn-sheldonize-default details-delete-button'))

    helper.layout = Layout(
            Field('name', placeholder="description for your meeting"),
            Field('start', placeholder="start meeting"),
            Field('end', placeholder="end meeting"),
            Field('repeat'),
            )   

    def __init__(self, *args, **kwargs):
        super(MeetingForm, self).__init__(*args, **kwargs)
        # if there is a due date on the Task instance you use to create this
        # task
        if self.instance.start and self.instance.end:
            # get that date and put it in the right timezone
            timezone = self.instance.user.userprofile.timezone.zone
            new_start = arrow.get(self.instance.start).to(timezone)
            new_end = arrow.get(self.instance.end).to(timezone)
            initial = kwargs.get('initial', {})
            initial['start'] = new_start.format("MM/DD/YYYY h:mm a")
            initial['end'] = new_end.format("MM/DD/YYYY h:mm a")
            kwargs['initial'] = initial


        super(MeetingForm, self).__init__(*args, **kwargs)

    def clean_start(self):
        form_start = self.cleaned_data['start']
        if form_start:
            timezone = self.instance.user.userprofile.timezone.zone
            new_arrow = arrow.get(form_start).replace(tzinfo=timezone)
            self.cleaned_data['start'] = new_arrow.datetime
        return self.cleaned_data['start']
 
    def clean_end(self):
        form_end = self.cleaned_data['end']
        if form_end:
            timezone = self.instance.user.userprofile.timezone.zone
            new_arrow = arrow.get(form_end).replace(tzinfo=timezone)
            self.cleaned_data['end'] = new_arrow.datetime
        return self.cleaned_data['end']
 

    class Meta:
        model = Meeting
        exclude = ('user',)

class AddMeetingForm(forms.Form):
    
#    start = DateTimeField(required=False,input_formats = ['%m/%d/%Y %I:%M %p'])
#    end = DateTimeField(required=False,input_formats = ['%m/%d/%Y %I:%M %p'])
#
    name = forms.CharField(max_length=140)

    helper = FormHelper()
    helper.form_class = 'form-horizontal sheldonize-form'
    helper.form_method = 'POST'
    helper.form_action = '.'
    helper.field_class = 'col-xs-12'

    helper.layout = Layout(
            FieldWithButtons(
                Field('name', placeholder="Quick add meetings"),
                StrictButton('<span class="glyphicon glyphicon-plus"></span>', type="submit", name="new_meeting", css_class='btn btn-sheldonize btn-sheldonize-default'))
            )

