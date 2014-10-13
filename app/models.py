from django.db import models
import engine.sort
import arrow

from django.contrib.auth.models import User

# for limiting values of the integers:
from django.core.validators import MinValueValidator, MaxValueValidator

# Google Authentication
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField
from oauth2client.django_orm import FlowField

size = models.IntegerField()

class Task(models.Model):
    WORK_ON_IT = (
            ('T', 'Today'),
            ('W', 'This Week'),
            )

    ABCD = (
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            )

    user = models.ForeignKey(User)
    name = models.CharField(verbose_name='name', max_length=140)
    comes_after = models.ForeignKey('self', verbose_name="after", null=True, blank=True, on_delete=models.SET_NULL)
    done = models.BooleanField(verbose_name='done?')
    topic = models.CharField(max_length=30, null=True, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    when = models.CharField(verbose_name='when?', max_length=1, choices=WORK_ON_IT, null=True, blank=True)
    # max for duration is 1 whole week (10080mins)
    duration = models.PositiveIntegerField(verbose_name='duration', null=True, blank=True, validators=[MinValueValidator(15), MaxValueValidator(10080)])
    created = models.DateTimeField(auto_now_add=True)
    done_date = models.DateTimeField(null=True, blank=True)
    # priority for the task
    priority = models.CharField(verbose_name='priority?', max_length=1, choices=ABCD, null=True, blank=True)

    def __unicode__(self):
        return self.name

    # we are going to override save to make sure the proper dates get saved.
    # Created is fine as this uses UTC on the server. However, the UI often
    # just sends for example 17:30. The model saves this as UTC, but it's not.
    # It's in the user's timezone, so we transform that to the proper timezone.
    def save(self, *args, **kwargs):
        if self.done:
            # if the task is done, make sure there are no scheduled items for
            # it:
            ScheduleItem.objects.filter(user=self.user, task=self).delete()
            # and it is removed from any comes_after
            comes_after_tasks = Task.objects.filter(user=self.user, comes_after=self)
            for t in comes_after_tasks:
                t.comes_after = None
                t.save()
            # Also set the when of a task to None if it's done
            self.when = None
            # Also set the done_date to "now" if done_date is null currently
            # (if it is not null, it means we already set a done date once, and
            # that's it)
            if not self.done_date:
                timezone = self.user.userprofile.timezone
                n = arrow.utcnow().to(timezone.zone)
                self.done_date = n.datetime
        else:
            # Make sure that the done_date gets removed (the user changed their
            # mind about whether this task was done or not)
            self.done_date = None

        super(Task, self).save(*args, **kwargs) # Call the "real" save() method.

    # to be able to check for class name in django templates
    def get_cname(self):
        return 'task'


class ScheduleItem(models.Model):

    STATUS = (
            (0,'OK'),
            (1,'Duration of Task not Satisfied'),
            (2,'Too Late'),
            )

    user = models.ForeignKey(User)
    task = models.ForeignKey(Task)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    status = models.PositiveIntegerField(default=0, choices=STATUS,)

    def __unicode__(self):
        return "scheduleitem for " + self.task.name

    # to be able to check for class name in django templates
    def get_cname(self):
        return 'scheduleitem'

class Preference(models.Model):
    DAYS = (
            (0,'Monday'),
            (1,'Tuesday'),
            (2,'Wednesday'),
            (3,'Thursday'),
            (4,'Friday'),
            (5,'Saturday'),
            (6,'Sunday'),
            )
 
    user = models.ForeignKey(User)
    day = models.PositiveIntegerField(verbose_name='day for work', choices=DAYS)
    from_time = models.TimeField(verbose_name='from')
    to_time = models.TimeField(verbose_name='to')

class Meeting(models.Model):

    user = models.ForeignKey(User)
    name = models.CharField(verbose_name='name', max_length=140)
    start = models.DateTimeField()
    end = models.DateTimeField()

    # for recurring meetings
    REPEAT = (
            (0, 'Daily'),
            (1, 'Every work day'),
            (2, 'Weekly'),
            (3, 'Every other week'),
            )

    FOREIGN = (
            (0, 'Google'),
            )

    repeat = models.PositiveIntegerField(verbose_name='repeat?', choices=REPEAT, null=True, blank=True)
    foreign = models.PositiveIntegerField(verbose_name='external?', choices=FOREIGN, null=True, blank=True)

    def __unicode__(self):
        return self.name

    # to be able to check for class name in django templates
    def get_cname(self):
        return 'meeting'


# Google Authentication

# South does not now these fields (we have to add introspection):

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^oauth2client\.django_orm\.CredentialsField"])
add_introspection_rules([], ["^oauth2client\.django_orm\.FlowField"])

class CredentialsModel(models.Model):
      id = models.ForeignKey(User, primary_key=True)
      credential = CredentialsField()

class FlowModel(models.Model):
      id = models.ForeignKey(User, primary_key=True)
      flow = FlowField()



