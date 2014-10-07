from django.contrib import admin
from django.core.mail import send_mail

import arrow
from models import UserProfile

from users.models import UserProfile, Wait, Invite

class UserProfileAdmin(admin.ModelAdmin):
    actions = ['reset_to_trial', 'send_me_betas', 'send_me_trials', 'send_me_undecided']
    list_display = ('user', 'usertype', 'daysleft', 'endperiod', 'timezone')

    def reset_to_trial(self, request, queryset):
        trial_userprofiles = UserProfile.objects.filter(usertype=1)
        for userprofile in trial_userprofiles:
            userprofile.user.is_active = True
            userprofile.usertype = 1
            userprofile.daysleft = 31
            userprofile.user.date_joined = arrow.utcnow().to(userprofile.timezone).datetime
            userprofile.user.save()
            userprofile.save()
    
        undecided_userprofiles = UserProfile.objects.filter(usertype=3)
        for userprofile in undecided_userprofiles:
            userprofile.user.is_active = True
            userprofile.usertype = 1
            userprofile.daysleft = 31
            userprofile.user.date_joined = arrow.utcnow().to(userprofile.timezone).datetime
            userprofile.user.save()
            userprofile.save()

    reset_to_trial.short_description = "Reset all trial or undecided users to be an initial trial user."

    def send_me_betas(self, request, queryset):
        beta_profiles = UserProfile.objects.filter(usertype=0)
        message = ""
        for p in beta_profiles:
            email = p.user.email
            message += email + ", "
        send_mail('Beta users Sheldonize', message , 'admin@sheldonize.com', ['stijn.heymans@gmail.com'], fail_silently=True)

    send_me_betas.short_description = "Send me all beta emails."

    def send_me_undecided(self, request, queryset):
        undecided_profiles = UserProfile.objects.filter(usertype=3)
        message = ""
        for p in undecided_profiles:
            email = p.user.email
            message += email + ", "
        send_mail('Undecided users Sheldonize', message , 'admin@sheldonize.com', ['stijn.heymans@gmail.com'], fail_silently=True)

    send_me_undecided.short_description = "Send me all undecided emails."

    def send_me_trials(self, request, queryset):
        trial_profiles = UserProfile.objects.filter(usertype=1)
        message = ""
        for p in trial_profiles:
            email = p.user.email
            message += email + ", "
        send_mail('Trial users Sheldonize', message , 'admin@sheldonize.com', ['stijn.heymans@gmail.com'], fail_silently=True)

    send_me_trials.short_description = "Send me all trial user emails."







class WaitAdmin(admin.ModelAdmin):
    list_display = ('email', 'on_list_date')

class InviteAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invited')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Wait, WaitAdmin)
admin.site.register(Invite, InviteAdmin)
