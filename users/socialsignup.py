from models import UserProfile, Invite
import pytz
import twitter_timezones
from app.service import create_default_preferences

def create_userprofile(backend, user, response, *args, **kwargs):
    # if the user is not there something went wrong, if the user profile is
    # already there, we already did all of this
    if user and not user.userprofile:
        user_profile = UserProfile.objects.create(user=user)

        # Social specific
        if backend.name == 'twitter':
            user_profile.timezone = pytz.timezone(twitter_timezones.zones[response.get('time_zone')])
            user_profile.social = True
            user_profile.socialtype = 1
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
            


