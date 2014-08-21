from django.test import TestCase
from app.models import Task, ScheduleItem
from users.models import UserProfile
import datetime
import arrow
from django.contrib.auth.models import User

class TaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('paul', 'mccarthy@thebeatles.com', 'paulpassword')
        self.userprofile = UserProfile.objects.create(user=self.user, timezone="America/Los_Angeles")
        self.userprofile2 = UserProfile.objects.create(user=self.user2, timezone="America/Los_Angeles")
        self.userprofile.save()
        self.userprofile2.save()
        self.now = arrow.utcnow().to(self.userprofile.timezone.zone)
        #self.tomorrow = self.now.replace(days=+1)
        #self.yesterday = self.now.replace(days=-1)
        #self.anhourago = self.now.replace(hours=-1)
        #self.inaminute = self.now.replace(minutes=+1)
        self.todo1 = Task.objects.create(user=self.user, name="todo1", done=False) 
        self.todo1.save()

    def tearDown(self):
        self.todo1.delete()
        self.userprofile.delete()
        self.userprofile2.delete()
        self.user.delete()
        self.user2.delete()

    def test_saving_done_1(self):
        # when saving a task and it is set to "done"
        # make sure it now has a done date as well
        self.assertFalse(self.todo1.done_date)
        self.todo1.done = True
        self.todo1.save()
        # now it has to have done_date
        self.assertFalse(not self.todo1.done_date)

    def test_saving_done_2(self):
        self.assertFalse(self.todo1.done_date)

        self.todo1.done = True
        self.todo1.save()
        # now it has a done date
        current_done = self.todo1.done_date

        # now set done AGAIN and save
        self.todo1.done = True
        self.todo1.save()
        # done date still has to be the same though
        self.assertEqual(self.todo1.done_date, current_done)
        # now remove done label
        self.todo1.done = False
        self.todo1.save()
        # done date also has to be gone
        self.assertFalse(self.todo1.done_date)
        # set done again
        self.todo1.done = True
        self.todo1.save()
        # now done date has to be back
        self.assertFalse(not self.todo1.done_date)





