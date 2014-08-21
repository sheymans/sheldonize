from django.db import models

from django.contrib.auth.models import User


class Subscription(models.Model):
    user = models.OneToOneField(User)
    stripe_id = models.CharField(max_length=255, unique=True)
