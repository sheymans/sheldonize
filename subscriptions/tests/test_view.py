from django.test import TestCase, Client
from django.core.urlresolvers import resolve
import app.parameters
from users.models import UserProfile
from django.contrib.auth.models import User
from django.conf import settings
from subscriptions.models import Subscription

import stripe
import arrow


class ViewTest(TestCase):
    def setUp(self):
        # use the TEST SECRET KEY for testing
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

        # the keys / have to be the test keys!
        settings.STRIPE_SECRET_KEY = settings.STRIPE_TEST_SECRET_KEY
        settings.STRIPE_PUBLIC_KEY = settings.STRIPE_TEST_PUBLIC_KEY

        self.client_stub = Client()
        self.user = User.objects.create_user('lennon', 'stijn.heymans+stripeviewstest@gmail.com', 'johnpassword')
        # set up a trial user
        self.userprofile = UserProfile.objects.create(user=self.user, timezone="America/Los_Angeles", usertype=1)

    def tearDown(self):
        settings.STRIPE_SECRET_KEY=settings.STRIPE_TEST_SECRET_KEY
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        self.userprofile.delete()
        self.user.delete()
        # get rid of all stripe customers created
        customers = stripe.Customer.all()
        for cust in customers.data:
            if cust.email == "stijn.heymans+stripeviewstest@gmail.com":
                cust.delete()


    def test_get_signup_subscriptions_logged_in_as_undecided(self):
        # test whether we can reach the signup page when we are an undecided user
        # (not just an undecided user)
        self.userprofile.usertype = 3
        self.userprofile.save()
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/subscriptions/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) > 0)
        first_template = response.templates[0]
        self.assertEqual(first_template.name, 'subscriptions/signup_subscription.html')

    def test_get_signup_subscriptions_logged_in_as_trial(self):
        # test whether we can reach the signup page when we are a trial user
        # (not just an undecided user)
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/subscriptions/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) > 0)
        first_template = response.templates[0]
        self.assertEqual(first_template.name, 'subscriptions/signup_subscription.html')

    def test_get_change_subscriptions_logged_in_as_trial(self):
        # You cannot change subscription as a trial user
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/subscriptions/change/')
        self.assertNotEqual(response.status_code, 200)

    def test_get_change_subscriptions_logged_in_as_undecided(self):
        # You cannot change subscription as a undecided user
        self.userprofile.usertype = 3
        self.userprofile.save()
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/subscriptions/change/')
        self.assertNotEqual(response.status_code, 200)

    def test_post_signup_subscription(self):
        
        # the user is a trial user
        self.assertTrue(self.userprofile.is_trial_user())
    
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        # now test
        self.assertEqual(response.status_code, 200)
        # a subscription must be created for that user
        self.assertTrue(Subscription.objects.filter(user=self.user).exists())
        # that subscribed user has the same email as this one
        self.assertEqual(Subscription.objects.get(user=self.user).user.email, email)
        # stripe created a customer with the right ID
        stripe_id = Subscription.objects.get(user=self.user).stripe_id
        customer = stripe.Customer.retrieve(stripe_id)

        # the user is now a pro user (but pick it up first again)
        self.userprofile = UserProfile.objects.get(user=self.user)
        self.assertTrue(self.userprofile.is_pro_user())

        # clean up
        Subscription.objects.all().delete()
        customer.delete()

    def test_post_signup_subscription_invalid_request(self):
        # messed up token
        email = 'stijn.heymans+stripeviewstest@gmail.com'
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': 'bullshittoken', 'stripeEmail': email})
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, ['Stripe: Invalid request.'])
 
    def test_post_signup_subscription_card_declined(self):
        
        # the user is a trial user
        self.assertTrue(self.userprofile.is_trial_user())
    
        token = stripe.Token.create(
            card={
                'number': '4000000000000127',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        # now test
        self.assertEqual(response.status_code, 200)
        # no subscription was created for that user
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())

        # the user is still a trial user
        self.userprofile = UserProfile.objects.get(user=self.user)
        self.assertTrue(self.userprofile.is_trial_user())

        # and finally we got a card_declined error
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, [u"Your card's security code is incorrect."])
 
        # clean up
        Subscription.objects.all().delete()

    def test_post_signup_subscription_authentication_error(self):
   
        # mess up the secret key
        orig = settings.STRIPE_SECRET_KEY
        settings.STRIPE_SECRET_KEY="messedup"
        
        # the user is a trial user
        self.assertTrue(self.userprofile.is_trial_user())
    
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        # now test
        self.assertEqual(response.status_code, 200)
        # no subscription was created for that user
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())

        # the user is still a trial user
        self.userprofile = UserProfile.objects.get(user=self.user)
        self.assertTrue(self.userprofile.is_trial_user())

        # and finally we got a authentication error
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, ['Stripe: Authentication Error.'])
 
        # clean up
        Subscription.objects.all().delete()
        settings.STRIPE_SECRET_KEY= orig

    def test_post_signup_subscription_no_token(self):
        # no token given
        email = 'stijn.heymans+stripeviewstest@gmail.com'
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeEmail': email})
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, ['Error: No token or email obtained from Stripe.'])
 
    def test_put_signup_subscription(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.put('/subscriptions/signup/', {})
        self.assertEqual(response.status_code, 404)
 
    def test_get_change_subscription(self):
        # First Create the Signup
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        # now test
        self.assertEqual(response.status_code, 200)

        # Now Get the change page
        response = self.client_stub.get('/subscriptions/change/')
        self.assertEqual(response.status_code, 200)
 
        # cleanup 
        stripe_id = Subscription.objects.get(user=self.user).stripe_id
        customer = stripe.Customer.retrieve(stripe_id)
        customer.delete()

    def test_get_change_subscription_deleted_customer(self):
    
        # First Create the Signup
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        # now test
        self.assertEqual(response.status_code, 200)

        # Now delete the customer to cause a 404 when getting the change page
        stripe_id = Subscription.objects.get(user=self.user).stripe_id
        customer = stripe.Customer.retrieve(stripe_id)
        customer.delete()

        # Now Get the change page
        response = self.client_stub.get('/subscriptions/change/')
        self.assertEqual(response.status_code, 404)
 
    def test_post_change_subscription_cancel_subscription(self):
    
        # First Create the Signup
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})
        stripe_id = Subscription.objects.get(user=self.user).stripe_id

        # now test
        self.assertEqual(response.status_code, 200)

        # Now post a cancel-subscription to the post page
        response = self.client_stub.post('/subscriptions/change/', {'cancel-subscription':''})
        self.assertEqual(response.status_code, 200)

        # now the user must be cancelled
        self.userprofile = UserProfile.objects.get(user=self.user)
        self.assertTrue(self.userprofile.is_cancelled_user())

        # The subscriptions for the user must be gone:
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())
        # and the customer is gone from stripe
	self.assertTrue(stripe.Customer.retrieve(stripe_id).deleted)


# Now the changing of the card:
    def test_post_change_subscription_change(self):
        
        # SIGN UP part
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})
        stripe_id = Subscription.objects.get(user=self.user).stripe_id

        # Change part
        token2 = stripe.Token.create(
            card={
                'number': '5555555555554444',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        response = self.client_stub.post('/subscriptions/change/', {'stripeToken': str(token2.id), 'stripeEmail': email})

        customer = stripe.Customer.retrieve(stripe_id)
        self.assertEqual(customer.cards.data[0].last4, '4444')

        # clean up
        Subscription.objects.all().delete()
        customer.delete()

    def test_post_change_subscription_invalid_request(self):
        # SIGN UP part
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
 
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        # messed up token
        response = self.client_stub.post('/subscriptions/change/', {'stripeToken': 'bullshittoken', 'stripeEmail': email})
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, ['Stripe: Invalid request.'])
 
    def test_post_change_subscription_card_declined(self):
         # SIGN UP part
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

       
        token2 = stripe.Token.create(
            card={
                'number': '4000000000000127',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
 
        response = self.client_stub.post('/subscriptions/change/', {'stripeToken': str(token2.id), 'stripeEmail': email})

        # now test
        self.assertEqual(response.status_code, 200)

        # and finally we got a card_declined error
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, [u"Your card's security code is incorrect."])
 
        # clean up
        Subscription.objects.all().delete()

    def test_post_change_subscription_no_token(self):
        # SIGN UP part
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})


        # no token given
        response = self.client_stub.post('/subscriptions/change/', {'stripeEmail': email})
        messages = response.context['messages']
        readable_messages = [ m.message for m in messages]
        self.assertEqual(readable_messages, ['Error: No token or email obtained from Stripe.'])
 
    def test_put_change_subscription(self):
        # SIGN UP part
        token = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        email = 'stijn.heymans+stripeviewstest@gmail.com'
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/subscriptions/signup/', {'stripeToken': str(token.id), 'stripeEmail': email})

        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.put('/subscriptions/change/', {})
        self.assertEqual(response.status_code, 404)
 
