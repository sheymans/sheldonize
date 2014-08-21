from django.contrib import admin

from subscriptions.models import Subscription

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_id')

admin.site.register(Subscription, SubscriptionAdmin)
