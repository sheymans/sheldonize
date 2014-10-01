from django.shortcuts import render
from django.conf import settings

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, Http404

from models import Subscription
from django.contrib import messages

import logging
import stripe
import json
import arrow


from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda user: user.userprofile.is_undecided_user() or user.userprofile.is_trial_user() or user.userprofile.is_cancelled_user(), login_url="/app/tasks")
def signup_subscription(request):
    if request.method == "GET":
        return render(request, 'subscriptions/signup_subscription.html', {'stripe_public_key': settings.STRIPE_PUBLIC_KEY}) 
    # Extra test on userprofile as cancelled users will not be shown the
    # subscribe buttons, but malicious users could try to post to the page
    # without that they  see it.
    elif request.method == "POST" and (request.user.userprofile.is_undecided_user() or request.user.userprofile.is_trial_user()):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if 'stripeToken' in request.POST and 'stripeEmail' in request.POST:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            try:
                # Create the subscription (this asks Stripe to try to
                # subscribe)
                customer = stripe.Customer.create( card=token, plan="sheldonizepro", email=email,) 
                # we always assume that upon subscription there is NO
                # Subscription object in Sheldonize
                subscription = Subscription.objects.create(user=request.user, stripe_id=customer.id)
                subscription.save()

                profile = request.user.userprofile
                profile.go_pro()
                success = "Your pro account has been created. Congratulations!"
                messages.add_message(request, messages.SUCCESS, success)
                return render(request, 'subscriptions/signup_subscription.html') 
                
            # see API: https://stripe.com/docs/api#errors
            except stripe.error.CardError, e: 
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body 
                err = body['error']
                error =  err['message']
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY}) 
        
            except stripe.error.InvalidRequestError, e:
                error = "Stripe: Invalid request."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except stripe.error.AuthenticationError, e:
                error = "Stripe: Authentication Error."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except stripe.error.APIConnectionError, e: # pragma: no cover
                error = "Stripe: Connection Error."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except stripe.error.StripeError, e: # pragma: no cover
                error = "Stripe: Error."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except Exception, e: # pragma: no cover
                error = "Uknown problem; if this problem persists contact support." + str(e)
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

        else:
            error="Error: No token or email obtained from Stripe."
            messages.add_message(request, messages.ERROR, error)
            return render(request, 'subscriptions/signup_subscription.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

    # not get or post
    else:
        raise Http404

@login_required
@user_passes_test(lambda user: user.userprofile.is_undecided_user() or user.userprofile.is_trial_user() or user.userprofile.is_cancelled_user(), login_url="/app/tasks")
def signup_student(request):
    if request.method == "GET":
        return render(request, 'subscriptions/signup_student.html', {'stripe_public_key': settings.STRIPE_PUBLIC_KEY}) 
    # Extra test on userprofile as cancelled users will not be shown the
    # subscribe buttons, but malicious users could try to post to the page
    # without that they  see it.
    elif request.method == "POST" and (request.user.userprofile.is_undecided_user() or request.user.userprofile.is_trial_user()):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if 'stripeToken' in request.POST and 'stripeEmail' in request.POST:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            try:
                # one time charge
                charge = stripe.Charge.create(amount=999, currency="usd", card=token, description=email)

                profile = request.user.userprofile
                profile.go_edu()
                success = "Your teacher and student account has been created. Congratulations!"
                messages.add_message(request, messages.SUCCESS, success)
                return render(request, 'subscriptions/signup_student.html') 
                
            # see API: https://stripe.com/docs/api#errors
            except stripe.error.CardError, e: 
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body 
                err = body['error']
                error =  err['message']
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY}) 
        
            except stripe.error.InvalidRequestError, e:
                error = "Stripe: Invalid request."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except stripe.error.AuthenticationError, e:
                error = "Stripe: Authentication Error."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except stripe.error.APIConnectionError, e: # pragma: no cover
                error = "Stripe: Connection Error."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except stripe.error.StripeError, e: # pragma: no cover
                error = "Stripe: Error."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            except Exception, e: # pragma: no cover
                error = "Uknown problem; if this problem persists contact support." + str(e)
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

        else:
            error="Error: No token or email obtained from Stripe."
            messages.add_message(request, messages.ERROR, error)
            return render(request, 'subscriptions/signup_student.html', { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

    # not get or post
    else:
        raise Http404






@login_required
@user_passes_test(lambda user: user.userprofile.is_pro_user(), login_url="/app/tasks/")
def change_subscription(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        stripe_id = request.user.subscription.stripe_id
        customer = stripe.Customer.retrieve(stripe_id)
        # this should normally not happen (if the user is a pro user, stripe
        # should have a subscription for him)
        subscription = customer.subscriptions.data[0]
    except:
        raise Http404

    valid_until_arrow = arrow.get(subscription.current_period_end).to(request.user.userprofile.timezone)
    valid_until = valid_until_arrow.date()

    if request.method == "GET":
        # first get the customer
        return render(request, 'subscriptions/change_subscription.html', {'customer': customer, 'valid_until': valid_until, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY })
    elif request.method == "POST":
        if 'cancel-subscription' in request.POST:
            try:
                # we are cancelling 
                request.user.userprofile.go_cancelled()

                # refund
                charges = stripe.Charge.all(customer=stripe_id)
                charges_data = charges.data
                
                if len(charges_data) <= 0: # pragma: no cover
                    messages.add_message(request, message.ERROR, "No previous charges are present. That's strange. Please contact sheldonizellc@gmail.com")
                    raise Http404

                charge = charges_data[0]
                try:
                    # establish refund
                    refund = charge.refunds.create()
                except: # pragma: no cover
                    error = "We could not create a refund on the last charge. Please contact sheldonizellc@gmail.com"
                    raise Http404

                # delete the STRIPE customer
                # According to the documentation this also deletes any active
                # subscriptions
                customer.delete()

                # delete the sheldy subscription
                sheldy_subscription = Subscription.objects.get(stripe_id=stripe_id)
                sheldy_subscription.delete()

                success = "Your subscription has been successfully cancelled. Your refund of 3.99$ should arrive within 5-10 business days." 
                messages.add_message(request, messages.SUCCESS, success)
                return render(request, 'subscriptions/change_subscription.html', {'stripe_public_key': settings.STRIPE_PUBLIC_KEY })

            except: # pragma: no cover
                error = "We could not cancel your subscription. Please try again or contact customer support."
                messages.add_message(request, messages.ERROR, error)
                return render(request, 'subscriptions/change_subscription.html', {'stripe_public_key': settings.STRIPE_PUBLIC_KEY })

        else:
            rendering_url = 'subscriptions/change_subscription.html'
            if 'stripeToken' in request.POST and 'stripeEmail' in request.POST:
                token = request.POST['stripeToken']
                email = request.POST['stripeEmail']
                try:
                    # we are updating the card with a token
                    customer.card = token
                    customer.save()
                    
                # see API: https://stripe.com/docs/api#errors
                except stripe.error.CardError, e: 
                    # Since it's a decline, stripe.error.CardError will be caught
                    body = e.json_body 
                    err = body['error']
                    error =  err['message']
                    messages.add_message(request, messages.ERROR, error)
                    return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
            
                except stripe.error.InvalidRequestError, e:
                    error = "Stripe: Invalid request."
                    messages.add_message(request, messages.ERROR, error)
                    return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
                except stripe.error.AuthenticationError, e: # pragma: no cover
                    error = "Stripe: Authentication Error."
                    messages.add_message(request, messages.ERROR, error)
                    return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
                except stripe.error.APIConnectionError, e: # pragma: no cover
                    error = "Stripe: Connection Error."
                    messages.add_message(request, messages.ERROR, error)
                    return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
                except stripe.error.StripeError, e: # pragma: no cover
                    error = "Stripe: Error."
                    messages.add_message(request, messages.ERROR, error)
                    return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 
                except Exception, e: # pragma: no cover
                    error = "Uknown problem; if this problem persists contact support."
                    messages.add_message(request, messages.ERROR, error)
                    return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

            else:
                error="Error: No token or email obtained from Stripe."
                messages.add_message(request, messages.ERROR, error)
                return render(request, rendering_url, { 'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

            success = "Your pro account has been successfully updated with your new data."
            messages.add_message(request, messages.SUCCESS, success)
            return render(request, rendering_url, { 'customer': customer, 'valid_until': valid_until,  'stripe_public_key': settings.STRIPE_PUBLIC_KEY }) 

    # not get or post
    else:
        raise Http404

# the webhook Stripe will send data to:
@csrf_exempt
@require_POST
def webhook(request):
    # write tests for these web hooks
    stripe.api_key = settings.STRIPE_SECRET_KEY
    event_json = json.loads(request.body)

    event_type = event_json['type']
    try:
        event = stripe.Event.retrieve(event_json['id'])
    except:
        # do not bother to continue when stripe is not able to retrieve the
        # event with this ID. That's strange and should be ignored.
        return HttpResponse(status=200)

    if not event:
        return HttpResponse(status=200)

    try:
        stripe_customer_id = event.data.object.customer
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)
        if Subscription.objects.filter(stripe_id=stripe_customer_id).exists():
            # it could indeed be that that subscription is already deleted
            # (when the user explicity cancelled)
            sheldy_subscription = Subscription.objects.get(stripe_id=stripe_customer_id)
            sheldy_user = sheldy_subscription.user
            email = sheldy_user.email
        else:
            email = None 
 
    except: 
        return HttpResponse(status=200)

    admin_email = 'admin@sheldonize.com'
    mesage_subject = ''
    message = ''

    if event_type == "invoice.payment_failed" or event_type == "charge.failed":
        if email:
            try:
                message_subject = 'Sheldonize: A problem with Your Payment'
                message = 'There seems to be a problem with your payment information. Please log in to sheldonize.com and check your payment information.'
                send_mail(message_subject, message, admin_email, [email, 'sheldonizellc@gmail.com'], fail_silently=True)
            except: # pragma: no cover
                logger.error("invoice.payment_failed or charge.failed email failed for " + email)

    elif event_type == "charge.refunded":
        # we are no longer sending an email as Stripe does that for us (see
        # stripe's account settings)
        return HttpResponse(status=200)
        #if email:
        #    try:
        #        message_subject = 'Sheldonize: Charge Refunded'
        #        message = '3.99$ was refunded to your account. This should arrive within 5-10 days on your account.'
        #        send_mail(message_subject, message, admin_email, [email, 'sheldonizellc@gmail.com'], fail_silently=True)
        #    except: # pragma: no cover
        #        logger.error("charge.refunded email failed for " + email)

    elif event_type == "customer.subscription.deleted":
        # this happens after failed attempts to invoice the customer (you can
        # specify that in the account settings of stripe, how many times)
        # the Subscription was deleted, at this point we want to also delete
        # the customer:
        try:

            # delete the STRIPE Customer (this also deletes the subscription)
            if event and stripe_customer:
                # IF there is an event then the user did NOT initiate this
                # subscription deleted, so this is always something to look at
                message_subject = 'Sheldonize: customer.subscription.deleted'
                message = 'Sheldonize webhook received a customer.subscription.deleted for ' + str(stripe_customer) + " (not initiated by user) "
                stripe_customer.delete()

            # delete the Sheldonize Subscription info if not done yet and
            # cancel the user
            if  event and sheldy_subscription and sheldy_user:
                # it could indeed be that that subscription is already deleted
                # (when the user explicity cancelled)
                sheldy_userprofile = sheldy_user.userprofile

                sheldy_subscription.delete()
                sheldy_userprofile.go_cancelled()
	
            
            if message_subject and message:
                # send message only to me: this is a failure to pay delete (not
                # initiated by user)
                send_mail(message_subject, message, admin_email, ['sheldonizellc@gmail.com'], fail_silently=True)
    
        except Exception as e: # pragma: no cover
            error_msg = "customer.subscription.deleted event failed for event %s: " % (event)
            logger.error(error_msg)

    # For now we don't care about other stuff
    # Always send back a 200
    return HttpResponse(status=200)
