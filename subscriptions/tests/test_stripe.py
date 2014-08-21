from django.test import TestCase
from django.core.urlresolvers import resolve
from subscriptions.models import Subscription
from users.models import UserProfile
from django.contrib.auth.models import User

from django.conf import settings
import stripe
import arrow
import time

class StripeTest(TestCase):
    def setUp(self):
        # use the TEST SECRET KEY for testing
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

        # further set the keys to TEST keys
        settings.STRIPE_SECRET_KEY = settings.STRIPE_TEST_SECRET_KEY
        settings.STRIPE_PUBLIC_KEY = settings.STRIPE_TEST_PUBLIC_KEY

        self.token1 = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
        self.customer1 = stripe.Customer.create( card=self.token1, plan="sheldonizepro", email="stijn.heymans+StripeTest@gmail.com")
        self.user1 = User.objects.create_user('stijn', 'stijn.heymans+StripeTest@gmail.com', 'test')
        self.userprofile1 = UserProfile.objects.create(user=self.user1, timezone="America/Los_Angeles")
        self.userprofile1.go_pro()
        self.userprofile1.save()
        self.subscription1 = Subscription.objects.create(user=self.user1, stripe_id=self.customer1.id)
        self.subscription1.save()

    def test_getting_subscription(self):
        sheldy_subscription = Subscription.objects.get(stripe_id=self.customer1.id)

    def test_subscription_deleted(self):
        customer = stripe.Customer.retrieve(self.subscription1.stripe_id)
        stripe_subscription = customer.subscriptions.data[0]
        self.userprofile1.go_cancelled()
        stripe_subscription.delete()


    def tearDown(self):
        self.customer1.delete()
        self.user1.delete()
        self.userprofile1.delete()
        self.subscription1.delete()


        
