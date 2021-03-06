from django.db import models

from django.contrib.auth.models import User
from timezone_field import TimeZoneField
import arrow

class UserProfile(models.Model):
    
    USER_TYPE = (
            (0, 'beta'),
            (1, 'trial'),
            (2, 'pro'),
            (3, 'undecided'),
            (4, 'cancelled'),
            (5, 'edu'),
            (6, 'free'),
            (7, 'donor'),
            )

    SOCIAL_TYPE = (
            (0, 'antisocial'),
            (1, 'twitter'),
            (2, 'facebook'),
            (3, 'google'),
            )

    THIS_WEEK = (
            (0, 'Mon-Sun'),
            (1, 'Tue-Mon'),
            (2, 'Wed-Tue'),
            (3, 'Thu-Wed'),
            (4, 'Fri-Thu'),
            (5, 'Sat-Fri'),
            (6, 'Sun-Sat'),
            )

    user = models.OneToOneField(User)
    timezone = TimeZoneField(default='America/Los_Angeles')
    # default user is 1 (trial user)
    usertype = models.PositiveIntegerField(choices=USER_TYPE, max_length=1, default=6)
    daysleft = models.PositiveIntegerField(default=31)
    # ENDPERIOD DEPRECATED; we are doing a refund instead
    endperiod = models.DateTimeField(null=True, blank=True)
    # how many successful invites did this user do (how people sign up that
    # this user invited)
    success_invites = models.PositiveIntegerField(default=0)
    # Verify whether this is a social account; in that case you should no ask
    # to change the password. Also not twitter users do not have an email!!!!
    # so you need to check on that whenever you need email.
    social = models.BooleanField(verbose_name='social?', default=False)
    socialtype = models.PositiveIntegerField(choices=SOCIAL_TYPE, max_length=1, default=0)
    # what constitues a week for a user (this will be his scheduling time)
    thisweek = models.PositiveIntegerField(choices=THIS_WEEK, max_length=1, default=0)
    # show deadlines on schedule or not (default is yes)
    showdeadlines = models.BooleanField(verbose_name='show deadlines on schedule?', default=True)

    def go_pro(self):
        self.user.is_active = True
        self.usertype = 2
        self.daysleft = 31
        self.user.save()
        self.save()


    def go_edu(self):
        self.user.is_active = True
        self.usertype = 5
        self.daysleft = 31
        self.user.save()
        self.save()

    def go_free(self):
        self.user.is_active = True
        self.usertype = 6
        self.daysleft = 31
        self.user.save()
        self.save()

    def go_donor(self):
        self.user.is_active = True
        self.usertype = 7
        self.daysleft = 31
        self.user.save()
        self.save()

    def go_undecided(self):
        self.user.is_active = False
        self.usertype = 3
        self.daysleft = 0
        self.user.save()
        self.save()

    def go_cancelled(self):
        # go cancelled is exactly like go undecided except that this is a user
        # who ones had a pro account.
        self.user.is_active = False
        self.usertype = 4
        self.daysleft = 0
        self.user.save()
        self.save()

    def all_permissions_granted(self):
        # make sure a trial goes to undecided if longer than a month
        self.evaluate_trial()
        return self.user.is_active and (self.usertype == 0 or self.usertype == 1 or self.usertype == 2 or self.usertype == 5 or self.usertype == 6 or self.usertype == 7)

    def is_cancelled_user(self):
        return self.usertype == 4

    def is_trial_user(self):
        return self.usertype == 1

    def is_beta_user(self):
        return self.usertype == 0

    def is_undecided_user(self):
        return self.usertype == 3

    def is_pro_user(self):
        return self.usertype == 2

    def is_social(self):
        return self.social

    def is_twitter_user(self):
        return self.socialtype == 1

    def is_facebook_user(self):
        return self.socialtype == 2

    def is_google_user(self):
        return self.socialtype == 3

    def is_edu_user(self):
        return self.usertype == 5

    def is_free_user(self):
        return self.usertype == 6

    def is_donor_user(self):
        return self.usertype == 7

    def evaluate_trial(self):
        if self.is_trial_user():
            zone = self.timezone
            now = arrow.utcnow().to(zone)
            joined = arrow.get(self.user.date_joined).to(zone)
            thirtyonedaysago = now.replace(days=-31)
            actualdaysleft = (joined - thirtyonedaysago).days + 1
            if actualdaysleft + (self.success_invites * 7) < 0:
                self.go_undecided()
            else:
                self.daysleft = actualdaysleft + ( self.success_invites * 7 )
                self.save()

# DEPRECATEDD
#    def evaluate_cancelled(self):
#        if self.is_cancelled_user():
#            zone = self.timezone
#            now = arrow.utcnow().to(zone)
#            endperiod = arrow.get(self.endperiod).to(zone)
#            if endperiod < now:
#                self.go_undecided()
#            else:
#                self.daysleft = (endperiod - now).days + 1
#                self.save()



### Waiting list of Interested Emails (they are not users yet!)

class Wait(models.Model):
    email = models.CharField(verbose_name='email', max_length=140)
    on_list_date = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return self.email # pragma: no cover


### Invites

class Invite(models.Model):
    inviter = models.ForeignKey(User)
    invited = models.CharField(verbose_name='email', max_length=140)
