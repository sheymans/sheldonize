from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, BaseInput
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from timezone_field import TimeZoneFormField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ChoiceField

from django.conf import settings

from models import Invite, UserProfile

import app.service

###############################################################################################
# https://github.com/maraujop/django-crispy-forms/issues/242
TEMPLATE_PACK = getattr(settings, 'CRISPY_TEMPLATE_PACK', 'bootstrap')
class SubmitButton(BaseInput):
    input_type = 'submit'
    field_classes = 'button' if TEMPLATE_PACK == 'uni_form' else 'btn' #removed btn-primary

################################################################################################


def unique_email_check(value):
    current = User.objects.filter(email__iexact=value)
    if current:
        raise ValidationError('This email address is already in use. Try another one please.')

def email_already_invited(value):
    # this ensures each email gets invited only once by one person
    if Invite.objects.filter(invited__iexact=value).exists():
        raise ValidationError('This email address was already invited. Try another friend!')

def friend_already_signed_up(value):
    current = User.objects.filter(email__iexact=value)
    if current:
        raise ValidationError('Your friend already signed up for Sheldonize. Try another friend!')

def unique_username_check(value):
    current = User.objects.filter(username__iexact=value)
    if current:
        raise ValidationError('This username is already in use. Try another one please.')

def allowed_email_check(value):
    forbidden_emails = [ 'stijn.heymans+support@gmail.com', 'sheldonizellc@gmail.com' ]
    if value in forbidden_emails:
        raise ValidationError('Sorry, this is a reserved email address.')


def max_users_reached(value):
    if app.service.free_registrations_left() <= 0:
        raise ValidationError('We have reached the maximum of free users we allow. Places become available daily. Please check back.')


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=30, validators=[unique_username_check])
    email = forms.EmailField(max_length=70, validators=[unique_email_check, allowed_email_check, max_users_reached])
    password = forms.CharField(max_length=28, widget=forms.PasswordInput())
    timezone = TimeZoneFormField()

    helper = FormHelper()
    helper.form_class='form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-3'
    helper.field_class = 'col-sm-9'
    helper.form_method = 'POST'

    helper.layout = Layout(
                Field('username', placeholder='choose a username', autofocus=True),
                Field('email', placeholder='youremail@example.com', autofocus=True),
                Field('password', placeholder='pick a password'),
                Field('timezone'),
            FormActions(
                SubmitButton('submit', 'Sign Up for Free', css_class='btn-sheldonize btn-sheldonize-primary'),
                ),
            )

class UserProfileForm(forms.Form):
    # Currently we only allow to change your timezone; all the rest we do not
    # care about.
    timezone = TimeZoneFormField()
    thisweek = ChoiceField(choices=UserProfile.THIS_WEEK, label="Your Week")

    helper = FormHelper()
    helper.form_class='form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.form_method = 'POST'

    helper.layout = Layout(
                Field('timezone'),
                Field('thisweek'),
            FormActions(
                SubmitButton('submit', 'Update', css_class='btn-sheldonize btn-sheldonize-primary'),
                ),
            )

class WaitForm(forms.Form):

    # Similar as signup form but without max users reached check
    email = forms.EmailField(max_length=70, validators=[unique_email_check, allowed_email_check])

    helper = FormHelper()
    helper.form_class='form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.form_method = 'POST'

    helper.layout = Layout(
                Field('email', placeholder='youremail@example.com', autofocus=True),
            FormActions(
                SubmitButton('submit', 'Add to Waiting List', css_class='btn-sheldonize btn-sheldonize-primary'),
                ),
            )

class InviteForm(forms.Form):

    # Similar as signup form but without max users reached check
    email = forms.EmailField(max_length=70, validators=[friend_already_signed_up, allowed_email_check, email_already_invited])

    helper = FormHelper()
    helper.form_class='form-horizontal sheldonize-form'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-10'
    helper.form_method = 'POST'

    helper.layout = Layout(
                Field('email', placeholder='person_to_invite@example.com', autofocus=True),
            FormActions(
                SubmitButton('submit', 'Invite to Sheldonize', css_class='btn-sheldonize btn-sheldonize-primary'),
                ),
            )


