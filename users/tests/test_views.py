from django.test import TestCase, Client
from django.core.urlresolvers import resolve
from users.models import UserProfile
from django.contrib.auth.models import User
from django.conf import settings

class ViewTest(TestCase):
    def setUp(self):

        self.client_stub = Client()

    def test_post_signup_has_to_be_trial_user(self):
        # when someone signs up, he has to be a trial user by default
        post_data = { 'username': 'trial_test_signup_1', 'email': 'trial_test_signup_1@test.com', 'password': 'test', 'timezone': 'America/Los_Angeles'}
        response = self.client_stub.post('/users/signup/', post_data )

        # check that the user now exists:
        self.assertTrue(User.objects.filter(username='trial_test_signup_1').exists())

        # Check that it is by default a trial user
        user = User.objects.get(username='trial_test_signup_1')
        self.assertTrue(user.userprofile.is_trial_user())

        # clean up get rid of user again
        User.objects.filter(username='trial_test_signup_1').delete()



