from django.test import TestCase
from users.models import UserProfile
import datetime
import arrow
from django.contrib.auth.models import User

class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        # create a trial user
        self.trialuserprofile = UserProfile.objects.create(user=self.user, timezone="America/Los_Angeles", usertype=1)
        self.trialuserprofile.save()

        self.now = arrow.utcnow().to(self.trialuserprofile.timezone.zone)
        self.tomorrow = self.now.replace(days=+1)

        self.cancelleduser = User.objects.create_user('paul', 'paul@thebeatles.com', 'paulpassword')
        self.cancelleduserprofile = UserProfile.objects.create(user=self.cancelleduser, timezone="America/Los_Angeles", usertype=4)
        self.cancelleduserprofile.save()

    def tearDown(self):
        self.user.delete()
        self.trialuserprofile.delete()
        self.cancelleduserprofile.delete()

    def test_new_trial_user(self):
        # verify that a new trial user has always 31 days left in trial.
        daysleft = self.trialuserprofile.daysleft
        self.assertEqual(daysleft, 31)

    def test_trial_user_after_evaluation(self):
        self.trialuserprofile.evaluate_trial()
        daysleft = self.trialuserprofile.daysleft
        self.assertEqual(daysleft, 31)

    def test_trial_user_joined_10_days_ago(self):
        # simulate that the user joined 10 days ago
        tendaysago = self.now.replace(days=-10)
        self.user.date_joined = tendaysago.datetime

        self.trialuserprofile.evaluate_trial()
        daysleft = self.trialuserprofile.daysleft
        self.assertEqual(daysleft, 21)

    def test_trial_user_joined_31_days_ago(self):
        # simulate that the user joined 31 days ago
        # this is the last trial day (days left should be 0)
        daysago = self.now.replace(days=-31)
        self.user.date_joined = daysago.datetime

        self.trialuserprofile.evaluate_trial()
        daysleft = self.trialuserprofile.daysleft
        self.assertEqual(daysleft, 0)

    def test_trial_user_joined_more_than_31_days_ago(self):
        # simulate that the user joined more than 31 days ago
        # trial is over: user is undecided, daysleft is 0
        daysago = self.now.replace(days=-32)
        self.user.date_joined = daysago.datetime

        self.trialuserprofile.evaluate_trial()
        daysleft = self.trialuserprofile.daysleft
        self.assertEqual(daysleft, 0)
        self.assertFalse(self.trialuserprofile.is_trial_user())
        self.assertTrue(self.trialuserprofile.is_undecided_user())

    def test_go_pro(self):
        self.trialuserprofile.go_pro()
        self.assertTrue(self.trialuserprofile.is_pro_user())

    def test_go_edu(self):
        self.trialuserprofile.go_edu()
        self.assertTrue(self.trialuserprofile.is_edu_user())


    def test_go_cancelled(self):
        self.trialuserprofile.go_pro()
        self.trialuserprofile.go_cancelled()
        self.assertTrue(self.trialuserprofile.is_cancelled_user())

    def test_all_permissions_granted(self):
        self.assertTrue(self.trialuserprofile.all_permissions_granted())

    def test_all_permissions_granted_edu_user(self):
        self.trialuserprofile.go_edu()
        self.assertTrue(self.trialuserprofile.all_permissions_granted())

        
