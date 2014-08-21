from django.contrib import admin

from users.models import UserProfile, Wait

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'usertype', 'daysleft', 'endperiod', 'timezone')

class WaitAdmin(admin.ModelAdmin):
    list_display = ('email', 'on_list_date')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Wait, WaitAdmin)
