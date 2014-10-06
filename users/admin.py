from django.contrib import admin

from users.models import UserProfile, Wait, Invite

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'usertype', 'daysleft', 'endperiod', 'timezone')

class WaitAdmin(admin.ModelAdmin):
    list_display = ('email', 'on_list_date')

class InviteAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invited')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Wait, WaitAdmin)
admin.site.register(Invite, InviteAdmin)
