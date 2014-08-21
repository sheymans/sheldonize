from django.test import TestCase, Client
from django.core.urlresolvers import resolve
import app.parameters
from users.models import UserProfile
from subscriptions.models import Subscription
from django.contrib.auth.models import User
import json
from django.conf import settings
import stripe
import arrow
import time

# for mail outbox
from django.core import mail

from mock import patch


class StripeWebhookTest(TestCase):
    def setUp(self):
        # use the TEST SECRET KEY for testing
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

        # the keys / have to be the test keys!
        settings.STRIPE_SECRET_KEY = settings.STRIPE_TEST_SECRET_KEY
        settings.STRIPE_PUBLIC_KEY = settings.STRIPE_TEST_PUBLIC_KEY

        self.client_stub = Client()
	# Create a pro user
        self.user_pro = User.objects.create_user('lennon', 'stijn.heymans+stripewebhooktest@gmail.com', 'johnpassword')
        self.userprofile_pro = UserProfile.objects.create(user=self.user_pro, timezone="America/Los_Angeles", usertype=2)
        self.token1 = stripe.Token.create(
            card={
                'number': '4242424242424242',
                'exp_month': '6',
                'exp_year': arrow.utcnow().datetime.year + 1,
                'cvc': '123',
            }
        )
       
 
    def tearDown(self):
        self.userprofile_pro.delete()
        self.user_pro.delete()

    @patch.object(stripe.Event, 'retrieve')
    def test_subscription_deleted(self, mock_retrieve):
        # we should not use the webhooks of stripe to test this (cause then we
        # have to have a webhook set up in stripe.com, and this would not run
        # as part of a test suite unfortunately). We also do not want the tests
        # to go to sheldonize.com
        # In other words we will only have a LIVE webhook on stripe.com to
        # sheldonize.com. Testing needs to simulate that.

        # so we need to mock up the retrieve event we have in the sheldonize
        # webhook view, to return something like below.


	# create customer via stripe API and Sheldonize Subscription object
	customer_pro = stripe.Customer.create( card=self.token1, plan="sheldonizepro", email="stijn.heymans+stripewebhooktest@gmail.com")
        # at this point we have a customer on a subscription on the STRIPE
        # side, now make a subscription on the Sheldonize side:
        subscription_pro = Subscription.objects.create(user=self.user_pro, stripe_id=customer_pro.id) 
        subscription_pro.save() 

	# Double check that these things now exist:
	self.assertTrue(Subscription.objects.filter(user=self.user_pro, stripe_id=customer_pro.id).exists())
	self.assertTrue(stripe.Customer.retrieve(customer_pro.id))
	# Check that this user is indeed a pro user
	self.assertTrue(self.userprofile_pro.is_pro_user())

	# Now create the subscription.customer.deleted event
        data =  {
                   "object":
                       {
                       "id": 'sub_4Zb8at43AX1YCK',
                       "plan":
                           {
                           "interval": "month",
                           "name": "Sheldonize Pro Account",
                           "created": 1407432186,
                           "amount": 399,
                           "currency": "usd",
                           "id": 'sheldonizepro',
                           "object": "plan",
                           "livemode": False,
                           "interval_count": 1,
                           "trial_period_days": None,
                           "metadata": {},
                           "statement_description": None,
                       },
                       "object": "subscription",
                       "start": 1407798623,
                       "status": "canceled",
                       "customer": str(customer_pro.id),
                       "cancel_at_period_end": False,
                       "current_period_start": 1407798623,
                       "current_period_end": 1410477023,
                       "ended_at": 1407798624,
                       "trial_start": None,
                       "trial_end": None,
                       "canceled_at": 1407798624,
                       "quantity": 1,
                       "application_fee_percent": None,
                       "discount": None,
                       "metadata": {},
                 }
             }
 
        event = {"id": "evt_14QSct45GGzZJVFJnLoNBmjb", "created": 1407801295, "livemode": False, "type": "customer.subscription.deleted", "data": data}

        # mock up what the webhook would normally ask stripe.com (webhooks
        # never use the data that was sent to webhook, only the id)
        # TODO we have to create an actual stripe event here, not just a dict
        mock_retrieve.return_value = stripe.Event.construct_from(event, settings.STRIPE_TEST_SECRET_KEY)

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
	# OK now test:
        self.assertEquals(response.status_code, 200)
	# user has to be cancelled now
	# we have to get it from the db though (it's changed in the background)
	self.userprofile_pro = UserProfile.objects.get(id=self.userprofile_pro.id)
	self.assertTrue(self.userprofile_pro.is_cancelled_user())
	
	# there can be no Sheldonize subscription object anymore
	self.assertFalse(Subscription.objects.filter(user=self.user_pro, stripe_id=customer_pro.id).exists())
	# And actually also the customer is gone from STRIPE (attribute 'deleted' set to true)
	self.assertTrue(stripe.Customer.retrieve(customer_pro.id).deleted)

        # Did a mail get send (in test mode django.core.mail does not actually
        # send email sends to an outbox)
        # https://docs.djangoproject.com/en/1.6/topics/testing/tools/#topics-testing-email
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Sheldonize: customer.subscription.deleted')


    @patch.object(stripe.Event, 'retrieve')
    def test_invoice_payment_failed(self, mock_retrieve):

	# create customer via stripe API and Sheldonize Subscription object
	customer_pro = stripe.Customer.create( card=self.token1, plan="sheldonizepro", email="stijn.heymans+stripewebhooktest@gmail.com")
        # at this point we have a customer on a subscription on the STRIPE
        # side, now make a subscription on the Sheldonize side:
        subscription_pro = Subscription.objects.create(user=self.user_pro, stripe_id=customer_pro.id) 
        subscription_pro.save() 

	# Double check that these things now exist:
	self.assertTrue(Subscription.objects.filter(user=self.user_pro, stripe_id=customer_pro.id).exists())
	self.assertTrue(stripe.Customer.retrieve(customer_pro.id))
	# Check that this user is indeed a pro user
	self.assertTrue(self.userprofile_pro.is_pro_user())

	# Now create the invoice.payment_failed event
        data =  {
                  "object": {
                    "date": 1407853982,
                    "id": "in_00000000000000",
                    "period_start": 1407853982,
                    "period_end": 1407853982,
                    "lines": {
                      "data": [
                        {
                          "id": "sub_4Zq4haTbwHuvyv",
                          "object": "line_item",
                          "type": "subscription",
                          "livemode": False,
                          "amount": 20000,
                          "currency": "usd",
                          "proration": False,
                          "period": {
                            "start": 1410532616,
                            "end": 1413124616
                          },
                          "quantity": 1,
                          "plan": {
                            "interval": "month",
                            "name": "Sheldonize Pro Account",
                            "created": 1407432186,
                            "amount": 399,
                            "currency": "usd",
                            "id": "sheldonizepro",
                            "object": "plan",
                            "livemode": False,
                            "interval_count": 1,
                            "trial_period_days": None,
                            "metadata": {},
                            "statement_description": None
                          },
                          "description": None,
                          "metadata": {}
                        }
                      ],
                      "count": 1,
                      "object": "list",
                      "url": "/v1/invoices/in_14QgKg45GGzZJVFJHLROXQQI/lines"
                    },
                    "subtotal": 399,
                    "total": 399,
                    "customer": str(customer_pro.id),
                    "object": "invoice",
                    "attempted": True,
                    "closed": False,
                    "forgiven": False,
                    "paid": False,
                    "livemode": False,
                    "attempt_count": 1,
                    "amount_due": 399,
                    "currency": "usd",
                    "starting_balance": 0,
                    "ending_balance": 0,
                    "next_payment_attempt": None,
                    "webhooks_delivered_at": 1407853982,
                    "charge": "ch_00000000000000",
                    "discount": None,
                    "application_fee": None,
                    "subscription": "sub_00000000000000",
                    "metadata": {},
                    "statement_description": None,
                    "description": None
                  }
                }
        event = {"id": "evt_14QSct45GGzZJVFJnLoNBmjb", "created": 1407801295, "livemode": False, "type": "invoice.payment_failed", "data": data}

        # mock up what the webhook would normally ask stripe.com (webhooks
        # never use the data that was sent to webhook, only the id)
        mock_retrieve.return_value = stripe.Event.construct_from(event, settings.STRIPE_TEST_SECRET_KEY)

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
        # Did a mail get send (in test mode django.core.mail does not actually
        # send email sends to an outbox)
        # https://docs.djangoproject.com/en/1.6/topics/testing/tools/#topics-testing-email
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Sheldonize: A problem with Your Payment')
        self.assertEqual(mail.outbox[0].to, ['stijn.heymans+stripewebhooktest@gmail.com', 'sheldonizellc@gmail.com'])

        # clean up
        try:
            customer_pro.delete()
            if Subscription.objects.filter(user=self.user_pro).exists():
                subscription_pro.delete()
        except: # pragma: no cover
            pass

    @patch.object(stripe.Event, 'retrieve')
    def test_charge_failed(self, mock_retrieve):

	# create customer via stripe API and Sheldonize Subscription object
	customer_pro = stripe.Customer.create( card=self.token1, plan="sheldonizepro", email="stijn.heymans+stripewebhooktest@gmail.com")
        # at this point we have a customer on a subscription on the STRIPE
        # side, now make a subscription on the Sheldonize side:
        subscription_pro = Subscription.objects.create(user=self.user_pro, stripe_id=customer_pro.id) 
        subscription_pro.save() 

	# Double check that these things now exist:
	self.assertTrue(Subscription.objects.filter(user=self.user_pro, stripe_id=customer_pro.id).exists())
	self.assertTrue(stripe.Customer.retrieve(customer_pro.id))
	# Check that this user is indeed a pro user
	self.assertTrue(self.userprofile_pro.is_pro_user())

	# Now create the charge_failed event
        data =  {
                    "object": {
                      "id": "ch_00000000000000",
                      "object": "charge",
                      "created": 1407853982,
                      "livemode": False,
                      "paid": False,
                      "amount": 399,
                      "currency": "usd",
                      "refunded": False,
                      "card": {
                        "id": "card_00000000000000",
                        "object": "card",
                        "last4": "4242",
                        "brand": "Visa",
                        "funding": "credit",
                        "exp_month": 6,
                        "exp_year": 2015,
                        "fingerprint": "p1NaskrhNdjgd1AI",
                        "country": "US",
                        "name": None,
                        "address_line1": None,
                        "address_line2": None,
                        "address_city": None,
                        "address_state": None,
                        "address_zip": None,
                        "address_country": None,
                        "cvc_check": "pass",
                        "address_line1_check": None,
                        "address_zip_check": None,
                        "customer": "cus_00000000000000"
                      },
                      "captured": True,
                      "refunds": {
                        "object": "list",
                        "total_count": 0,
                        "has_more": False,
                        "url": "/v1/charges/ch_14QgKg45GGzZJVFJ5PSbUHU5/refunds",
                        "data": []
                      },
                      "balance_transaction": "txn_00000000000000",
                      "failure_message": None,
                      "failure_code": None,
                      "amount_refunded": 0,
                      "customer": str(customer_pro.id),
                      "invoice": "in_00000000000000",
                      "description": None,
                      "dispute": None,
                      "metadata": {},
                      "statement_description": None,
                      "receipt_email": None
                    }
                } 
        
        
        
        event = {"id": "evt_14QSct45GGzZJVFJnLoNBmjb", "created": 1407801295, "livemode": False, "type": "charge.failed", "data": data}

        # mock up what the webhook would normally ask stripe.com (webhooks
        # never use the data that was sent to webhook, only the id)
        mock_retrieve.return_value = stripe.Event.construct_from(event, settings.STRIPE_TEST_SECRET_KEY)

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
        # Did a mail get send (in test mode django.core.mail does not actually
        # send email sends to an outbox)
        # https://docs.djangoproject.com/en/1.6/topics/testing/tools/#topics-testing-email
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Sheldonize: A problem with Your Payment')
        self.assertEqual(mail.outbox[0].to, ['stijn.heymans+stripewebhooktest@gmail.com', 'sheldonizellc@gmail.com'])

        # clean up
        try:
            customer_pro.delete()
            if Subscription.objects.filter(user=self.user_pro).exists():
                subscription_pro.delete()
        except: # pragma: no cover
            pass

    @patch.object(stripe.Event, 'retrieve')
    def test_charge_refunded(self, mock_retrieve):

	# create customer via stripe API and Sheldonize Subscription object
	customer_pro = stripe.Customer.create( card=self.token1, plan="sheldonizepro", email="stijn.heymans+stripewebhooktest@gmail.com")
        # at this point we have a customer on a subscription on the STRIPE
        # side, now make a subscription on the Sheldonize side:
        subscription_pro = Subscription.objects.create(user=self.user_pro, stripe_id=customer_pro.id) 
        subscription_pro.save() 

	# Double check that these things now exist:
	self.assertTrue(Subscription.objects.filter(user=self.user_pro, stripe_id=customer_pro.id).exists())
	self.assertTrue(stripe.Customer.retrieve(customer_pro.id))
	# Check that this user is indeed a pro user
	self.assertTrue(self.userprofile_pro.is_pro_user())

	# Now create the charge.refunded event
        data =  {
            "object": {
              "id": "ch_00000000000000",
              "object": "charge",
              "created": 1407853982,
              "livemode": False,
              "paid": True,
              "amount": 399,
              "currency": "usd",
              "refunded": True,
              "card": {
                "id": "card_00000000000000",
                "object": "card",
                "last4": "4242",
                "brand": "Visa",
                "funding": "credit",
                "exp_month": 6,
                "exp_year": 2015,
                "fingerprint": "p1NaskrhNdjgd1AI",
                "country": "US",
                "name": None,
                "address_line1": None,
                "address_line2": None,
                "address_city": None,
                "address_state": None,
                "address_zip": None,
                "address_country": None,
                "cvc_check": "pass",
                "address_line1_check": None,
                "address_zip_check": None,
                "customer": "cus_00000000000000"
              },
              "captured": True,
              "refunds": {
                "object": "list",
                "total_count": 0,
                "has_more": False,
                "url": "/v1/charges/ch_14QgKg45GGzZJVFJ5PSbUHU5/refunds",
                "data": [
                  {
                    "id": "re_4Zq3jpp9lmrfHS",
                    "amount": 399,
                    "currency": "usd",
                    "created": 1407854165,
                    "object": "refund",
                    "charge": "ch_4Zq3TnoodKLMm1",
                    "balance_transaction": "txn_4Zq3cMA9MwvuIO",
                    "metadata": {}
                  }
                ]
              },
              "balance_transaction": "txn_00000000000000",
              "failure_message": None,
              "failure_code": None,
              "amount_refunded": 399,
              "customer": str(customer_pro.id),
              "invoice": "in_00000000000000",
              "description": None,
              "dispute": None,
              "metadata": {},
              "statement_description": None,
              "receipt_email": None,
              "fee": 0
            }
          }        
        
        
        event = {"id": "evt_14QSct45GGzZJVFJnLoNBmjb", "created": 1407801295, "livemode": False, "type": "charge.refunded", "data": data}

        # mock up what the webhook would normally ask stripe.com (webhooks
        # never use the data that was sent to webhook, only the id)
        mock_retrieve.return_value = stripe.Event.construct_from(event, settings.STRIPE_TEST_SECRET_KEY)

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
        self.assertEqual(response.status_code, 200)
	
        # Did a mail get send (in test mode django.core.mail does not actually
        # send email sends to an outbox)
        # https://docs.djangoproject.com/en/1.6/topics/testing/tools/#topics-testing-email
        # Test that one message has been sent.
        # NOTE: we are no longer sending email in the charge.refund webhook as
        # we set strip to do that
        #self.assertEqual(len(mail.outbox), 1)
        #self.assertEqual(mail.outbox[0].subject, 'Sheldonize: Charge Refunded')
        #self.assertEqual(mail.outbox[0].to, ['stijn.heymans+stripewebhooktest@gmail.com', 'sheldonizellc@gmail.com'])

        # clean up
        try:
            customer_pro.delete()
            if Subscription.objects.filter(user=self.user_pro).exists():
                subscription_pro.delete()
        except: # pragma: no cover
            pass

    def test_no_retrievable_event(self):
        data =  {}
        # no event id 
        event = {"id": "evt_bullshitID", "created": 1407801295, "livemode": False, "type": "customer.subscription.deleted", "data": data}

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
	# OK now test:
        self.assertEquals(response.status_code, 200)
	
    @patch.object(stripe.Event, 'retrieve')
    def test_event_is_none(self, mock_retrieve):
        event = {"id": "evt_bullshitID", "created": 1407801295, "livemode": False, "type": "customer.subscription.deleted", "data": {}}
        # event is None when verified
        mock_retrieve.return_value = None

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
	# OK now test:
        self.assertEquals(response.status_code, 200)
	
    @patch.object(stripe.Event, 'retrieve')
    def test_charge_refunded_no_email(self, mock_retrieve):

	# create customer via stripe API and Sheldonize Subscription object
	customer_pro = stripe.Customer.create( card=self.token1, plan="sheldonizepro", email="stijn.heymans+stripewebhooktest@gmail.com")
        # HOWEVER we do not create a Subscription on the Sheldonize side, so
        # there will not be an email to be picked up

	self.assertTrue(stripe.Customer.retrieve(customer_pro.id))

	# Now create the charge.refunded event
        data =  {
            "object": {
              "id": "ch_00000000000000",
              "object": "charge",
              "created": 1407853982,
              "livemode": False,
              "paid": True,
              "amount": 399,
              "currency": "usd",
              "refunded": True,
              "card": {
                "id": "card_00000000000000",
                "object": "card",
                "last4": "4242",
                "brand": "Visa",
                "funding": "credit",
                "exp_month": 6,
                "exp_year": 2015,
                "fingerprint": "p1NaskrhNdjgd1AI",
                "country": "US",
                "name": None,
                "address_line1": None,
                "address_line2": None,
                "address_city": None,
                "address_state": None,
                "address_zip": None,
                "address_country": None,
                "cvc_check": "pass",
                "address_line1_check": None,
                "address_zip_check": None,
                "customer": "cus_00000000000000"
              },
              "captured": True,
              "refunds": {
                "object": "list",
                "total_count": 0,
                "has_more": False,
                "url": "/v1/charges/ch_14QgKg45GGzZJVFJ5PSbUHU5/refunds",
                "data": [
                  {
                    "id": "re_4Zq3jpp9lmrfHS",
                    "amount": 399,
                    "currency": "usd",
                    "created": 1407854165,
                    "object": "refund",
                    "charge": "ch_4Zq3TnoodKLMm1",
                    "balance_transaction": "txn_4Zq3cMA9MwvuIO",
                    "metadata": {}
                  }
                ]
              },
              "balance_transaction": "txn_00000000000000",
              "failure_message": None,
              "failure_code": None,
              "amount_refunded": 399,
              "customer": str(customer_pro.id),
              "invoice": "in_00000000000000",
              "description": None,
              "dispute": None,
              "metadata": {},
              "statement_description": None,
              "receipt_email": None,
              "fee": 0
            }
          }        
        
        
        event = {"id": "evt_14QSct45GGzZJVFJnLoNBmjb", "created": 1407801295, "livemode": False, "type": "charge.refunded", "data": data}

        # mock up what the webhook would normally ask stripe.com (webhooks
        # never use the data that was sent to webhook, only the id)
        mock_retrieve.return_value = stripe.Event.construct_from(event, settings.STRIPE_TEST_SECRET_KEY)

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
        # no email got sent cause we were not able to set an email
        self.assertEqual(len(mail.outbox), 0)
        self.assertEquals(response.status_code, 200)

        # clean up
        try:
            customer_pro.delete()
            if Subscription.objects.filter(user=self.user_pro).exists():
                subscription_pro.delete()
        except: # pragma: no cover
            pass

    @patch.object(stripe.Event, 'retrieve')
    def test_charge_refunded_no_retrievable_customer(self, mock_retrieve):

        # we did not create a customer so the customer retrieval will fail (we
        # added a fake "customer" in data below)

	# Now create the charge.refunded event
        data =  {
            "object": {
              "id": "ch_00000000000000",
              "object": "charge",
              "created": 1407853982,
              "livemode": False,
              "paid": True,
              "amount": 399,
              "currency": "usd",
              "refunded": True,
              "card": {
                "id": "card_00000000000000",
                "object": "card",
                "last4": "4242",
                "brand": "Visa",
                "funding": "credit",
                "exp_month": 6,
                "exp_year": 2015,
                "fingerprint": "p1NaskrhNdjgd1AI",
                "country": "US",
                "name": None,
                "address_line1": None,
                "address_line2": None,
                "address_city": None,
                "address_state": None,
                "address_zip": None,
                "address_country": None,
                "cvc_check": "pass",
                "address_line1_check": None,
                "address_zip_check": None,
                "customer": "cus_00000000000000"
              },
              "captured": True,
              "refunds": {
                "object": "list",
                "total_count": 0,
                "has_more": False,
                "url": "/v1/charges/ch_14QgKg45GGzZJVFJ5PSbUHU5/refunds",
                "data": [
                  {
                    "id": "re_4Zq3jpp9lmrfHS",
                    "amount": 399,
                    "currency": "usd",
                    "created": 1407854165,
                    "object": "refund",
                    "charge": "ch_4Zq3TnoodKLMm1",
                    "balance_transaction": "txn_4Zq3cMA9MwvuIO",
                    "metadata": {}
                  }
                ]
              },
              "balance_transaction": "txn_00000000000000",
              "failure_message": None,
              "failure_code": None,
              "amount_refunded": 399,
              "customer": "cus_00000000000000",
              "invoice": "in_00000000000000",
              "description": None,
              "dispute": None,
              "metadata": {},
              "statement_description": None,
              "receipt_email": None,
              "fee": 0
            }
          }        
        
        
        event = {"id": "evt_14QSct45GGzZJVFJnLoNBmjb", "created": 1407801295, "livemode": False, "type": "charge.refunded", "data": data}

        # mock up what the webhook would normally ask stripe.com (webhooks
        # never use the data that was sent to webhook, only the id)
        mock_retrieve.return_value = stripe.Event.construct_from(event, settings.STRIPE_TEST_SECRET_KEY)

        msg = json.dumps(event)
        response = self.client_stub.post( '/subscriptions/webhook/', msg, content_type="application/json")
	
        self.assertEquals(response.status_code, 200)

