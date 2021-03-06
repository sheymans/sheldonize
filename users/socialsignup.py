from models import UserProfile, Invite
import pytz
import twitter_timezones
from app.service import create_default_preferences

def create_userprofile(backend, user, response, *args, **kwargs):
    # if the user is not there something went wrong, if the user profile is
    # already there, we already did all of this
    if user and not UserProfile.objects.filter(user=user).exists():
        user_profile = UserProfile.objects.create(user=user)
        user_profile.save()

        # Social specific
        if backend.name == 'twitter':
            timez = response.get('time_zone')
            if timez and timez in twitter_timezones.zones:
                user_profile.timezone = pytz.timezone(twitter_timezones.zones[timez])
            else:
                user_profile.timezone = pytz.timezone("America/Los_Angeles")
            user_profile.social = True
            user_profile.socialtype = 1
            user_profile.save()

        if backend.name == 'google-oauth2':
            # Google does not send timezone
            user_profile.timezone = pytz.timezone("America/Los_Angeles")
            user_profile.social = True
            user_profile.socialtype = 3
            user_profile.save()


        # Facebook (Also set email here)

        # create the default preferences
        create_default_preferences(user)

        # cross check invites; note that twitter users do not have emails so
        # they do not count toward invites
        if not user_profile.is_twitter_user():
            email = user.email
            if Invite.objects.filter(invited__iexact=email).exists():
                invite = Invite.objects.filter(invited__iexact=email)[0]
                inviter = invite.inviter
                inviter.userprofile.success_invites += 1
                # also evaluate trial of that inviter to make sure he gets his
                # daysleft immediately correct (without that he has to press
                # preferences or so)
                inviter.userprofile.evaluate_trial()
                inviter.userprofile.save()
            


