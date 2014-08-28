from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth import authenticate
from django.contrib import messages
from app.views import tasks, home, clean_up_authentication
from subscriptions.views import signup_subscription
from app.service import create_default_preferences
from forms import SignUpForm, UserProfileForm, WaitForm
from django.contrib.auth.models import User
from models import UserProfile, Wait
from django.contrib.auth import authenticate, login, logout
import arrow

import hashlib

# this simulates login_required keyword
from braces.views import LoginRequiredMixin

def login_v(request):

    logout(request)

    # for when the login fails:
    bad_login = False
    # where to go next when login succeeds
    next = None
    if request.GET:
        next = request.GET.get('next','')

    if request.POST:
        # we want the username to be the email
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            # we'll log the user in, but depending on what he can do further we
            # relay him to the pay site
            login(request, user)
            if user.userprofile.all_permissions_granted():
                # send it off to the "next" location or to tasks 
                # 2nd argument is default
                if next:
                    return redirect(next)
                else:
                    return redirect(tasks)
            # Else user is no longer allowed to login, guide to paying page:
            else:
                return redirect(signup_subscription)
        else:
            bad_login = True

    return render(request, 'users/login.html', {'bad_login': bad_login, 'next': next})

def logout_v(request):
    clean_up_authentication(request.user)
    logout(request)
    return redirect(home)


def thanks(request):
    return render(request, 'users/thanks.html')

# this is a class-based view
class SignupView(FormView):
    # form_valid redirects automatically to this url
    success_url = '/app/tasks/'
    form_class = SignUpForm
    template_name = 'users/signup.html'

    def get_initial(self):
        logout(self.request)
        if self.request.GET:
            # default is Los_Angeles
            timezone = self.request.GET.get('timezone','America/Los_Angeles')
            return { 'timezone' : timezone }
        else:
            return {}

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.full_clean()

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']

            # this also saves the user
            # Do not use email as username as the latter can be 75 chars and
            # the former only 30
            user = User.objects.create_user(username, email, password)

            user_profile = UserProfile.objects.create(user=user)
            user_profile.timezone = form.cleaned_data['timezone']
            user_profile.save()

            # Create default preferences for that user (mo-fri 9-5)
            create_default_preferences(user)

            # now authenticate the user
            user_auth = authenticate(username=username, password=password)
            login(request, user_auth)

            # cross check waiting list and remove the email from the waiting
            # list (we signed up that user)
            Wait.objects.filter(email=email).delete()
            
            return self.form_valid(form)

        else:
            return self.form_invalid(form)


class UserProfileView(LoginRequiredMixin, FormView):
    success_url = '/app/tasks/'
    form_class = UserProfileForm
    template_name = 'users/userprofile.html'

    def get_initial(self):
        user = self.request.user
        userprofile = user.userprofile

        return {
                'timezone': userprofile.timezone,
                }

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Profile updated.')
        return super(UserProfileView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.full_clean()

        if form.is_valid():
            user = self.request.user
            user.userprofile.timezone = form.cleaned_data['timezone']
            user.userprofile.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class WaitView(FormView):
    success_url = '/users/wait/thanks/'
    form_class = WaitForm
    template_name = 'users/wait.html'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Email added on the waiting list.')
        return super(WaitView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.full_clean()

        if form.is_valid():
            w = Wait.objects.create(email=form.cleaned_data['email'], on_list_date=arrow.utcnow().datetime)
            w.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
