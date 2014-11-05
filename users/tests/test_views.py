from django.test import TestCase, Client
from django.core.urlresolvers import resolve
from users.models import UserProfile, Invite
from django.contrib.auth.models import User
from django.conf import settings

class ViewTest(TestCase):
    def setUp(self):

        self.client_stub = Client()

    def tearDown(self):
        Invite.objects.all().delete()
        

    def test_post_signup_has_to_be_free_user(self):
        # when someone signs up, he has to be a free user by default
        post_data = { 'username': 'trial_test_signup_1', 'email': 'trial_test_signup_1@test.com', 'password': 'test', 'timezone': 'America/Los_Angeles'}
        response = self.client_stub.post('/users/signup/', post_data )

        # check that the user now exists:
        self.assertTrue(User.objects.filter(username='trial_test_signup_1').exists())

        # Check that it is by default a free user
        user = User.objects.get(username='trial_test_signup_1')
        self.assertTrue(user.userprofile.is_free_user())

        # clean up get rid of user again
        User.objects.filter(username='trial_test_signup_1').delete()
 

    def test_invite_already_a_user(self):
        self.user = User.objects.create_user('lennon', 'lennon@thebeatles.com', 'johnpassword')
        # trial user:
        self.userprofile = UserProfile.objects.create(user=self.user, usertype=1, timezone="America/Los_Angeles")
        self.client_stub.login(username='lennon', password='johnpassword')

        response = self.client_stub.post('/users/invite/', {'email': 'lennon@thebeatles.com'})
        self.assertEqual(response.status_code, 200)

    def test_invite_already_invited(self):
        self.user = User.objects.create_user('lennon', 'lennon@thebeatles.com', 'johnpassword')
        # trial user:
        self.userprofile = UserProfile.objects.create(user=self.user, usertype=1, timezone="America/Los_Angeles")
        self.client_stub.login(username='lennon', password='johnpassword')

        Invite.objects.create(inviter=self.user, invited='paul@thebeatles.com')
        self.assertTrue(Invite.objects.filter(invited__iexact='paul@thebeatles.com').exists())

        response = self.client_stub.post('/users/invite/', {'email': 'paul@thebeatles.com'})
        self.assertEqual(response.status_code, 200)

        # does not get added 2 times
        self.assertTrue(Invite.objects.filter(invited__iexact='paul@thebeatles.com').count() == 1)

    def test_invite_successful_invite(self):
        self.user = User.objects.create_user('lennon', 'lennon@thebeatles.com', 'johnpassword')
        # trial user:
        self.userprofile = UserProfile.objects.create(user=self.user, usertype=1, timezone="America/Los_Angeles")
        self.client_stub.login(username='lennon', password='johnpassword')

        response = self.client_stub.post('/users/invite/', {'email': 'paul@thebeatles.com'})
        # should be a redirect
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Invite.objects.filter(invited__iexact='paul@thebeatles.com').exists())

