from django.test import TestCase
import app.service 
from app.models import Task, ScheduleItem, Meeting, Preference
from users.models import UserProfile
import datetime
import arrow
import app.parameters
from django.contrib.auth.models import User
from timer import Timer

class ServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('paul', 'mccarthy@thebeatles.com', 'paulpassword')
        # betas
        self.userprofile = UserProfile.objects.create(user=self.user, usertype=0, timezone="America/Los_Angeles")
        self.userprofile2 = UserProfile.objects.create(user=self.user2, usertype=0, timezone="America/Los_Angeles")
        self.userprofile.save()
        self.userprofile2.save()
        self.now = arrow.utcnow().to(self.userprofile.timezone.zone)
        self.tomorrow = self.now.replace(days=+1)
        self.nextweek = self.now.replace(days=+7)
        self.yesterday = self.now.replace(days=-1)
        self.anhourago = self.now.replace(hours=-1)
        self.inaminute = self.now.replace(minutes=+1)
        self.todo1 = Task.objects.create(user=self.user, name="todo1", done=False, due=self.tomorrow.datetime,when='W', duration=76)
        self.todo2 = Task.objects.create(user=self.user, name="todo2", done=False, due=self.tomorrow.datetime,when='T')
        self.todo3 = Task.objects.create(user=self.user, name="todo3", done=False, due=self.tomorrow.datetime)
        self.todo4 = Task.objects.create(user=self.user, name="todo4", done=True, due=self.tomorrow.datetime,when='T')
        self.todo5 = Task.objects.create(user=self.user, name="todo5", done=False, due=self.anhourago.datetime,when='T')
        self.todo6 = Task.objects.create(user=self.user, name="todo6", done=False, due=self.yesterday.datetime,when='W')
        self.todo7 = Task.objects.create(user=self.user, name="todo7", done=False, due=self.inaminute.datetime,when='W')

        self.todo8 = Task.objects.create(user=self.user, name="todo8", done=False, due=self.inaminute.datetime,when=None, comes_after=self.todo7)

        self.preference1 = Preference.objects.create(user=self.user, day=0, from_time="09:00", to_time="17:00")
        self.preference2 = Preference.objects.create(user=self.user, day=1, from_time="09:00", to_time="17:00")
        self.preference3 = Preference.objects.create(user=self.user, day=2, from_time="09:00", to_time="17:00")
        self.preference4 = Preference.objects.create(user=self.user, day=3, from_time="09:00", to_time="17:00")
        self.preference5 = Preference.objects.create(user=self.user, day=4, from_time="09:00", to_time="17:00")
        self.preference6 = Preference.objects.create(user=self.user, day=5, from_time="09:00", to_time="17:00")
        self.preference7 = Preference.objects.create(user=self.user, day=6, from_time="09:00", to_time="17:00")
        self.preference1.save()
        self.preference2.save()
        self.preference3.save()
        self.preference4.save()
        self.preference5.save()
        self.preference6.save()
        self.preference7.save()


        self.todo1.save()
        self.todo2.save()
        self.todo3.save()
        self.todo4.save()
        self.todo5.save()
        self.todo6.save()
        self.todo7.save()
        self.todo8.save()


        self.meeting1 = Meeting.objects.create(user=self.user, name="Meeting 1", start="2014-08-11 11:00:00-07:00", end="2014-08-11 12:00:00-07:00")
        self.meeting2 = Meeting.objects.create(user=self.user, name="Meeting 2", start="2016-08-11 11:00:00-07:00", end="2016-08-11 13:00:00-07:00")
        self.meeting1.save()
        self.meeting2.save()

        self.tomorrowminus1 = self.tomorrow.replace(hours=-1)
        self.sch1 = ScheduleItem.objects.create(user=self.user, task=self.todo1, from_date=self.tomorrowminus1.datetime, to_date=self.tomorrow.datetime) 
        self.sch1.save()


        
        self.sch2 = ScheduleItem.objects.create(user=self.user, task=self.todo1, from_date="2014-08-11 11:00:00-07:00", to_date="2014-08-11 12:00:00-07:00", status=1)
        self.sch3 = ScheduleItem.objects.create(user=self.user, task=self.todo1, from_date="2014-08-11 11:00:00-07:00", to_date="2014-08-11 11:15:00-07:00", status=2)
        self.sch2.save()
        self.sch3.save()


    def tearDown(self):
        self.todo1.delete()
        self.todo2.delete()
        self.todo3.delete()
        self.todo4.delete()
        self.todo5.delete()
        self.todo6.delete()
        self.todo7.delete()
        self.sch1.delete()
        self.meeting1.delete()
        self.meeting2.delete()
        self.sch2.delete()
        self.sch3.delete()
        self.todo8.delete()

        self.preference1.delete()
        self.preference2.delete()
        self.preference3.delete()
        self.preference4.delete()
        self.preference5.delete()
        self.preference6.delete()
        self.preference7.delete()


    def test_tasks_2_dict(self):
        all_tasks = Task.objects.all()
        tasks_dict = app.service.tasks_2_dict(all_tasks, "America/Los_Angeles")
        self.assertTrue(tasks_dict is not None)

    def test_meetings_2_dict(self):
        all_meetings = Meeting.objects.all()
        meetings_dict = app.service.meetings_2_dict(all_meetings, "America/Los_Angeles")
        self.assertTrue(meetings_dict is not None)


    def test_scheduleitems_2_dict(self):
        selected = app.service.get_tasks_to_schedule(self.user, self.now, "America/Los_Angeles")
        scheduled_dict = app.service.scheduleitems_2_dict(ScheduleItem.objects.filter(task__in=selected), "America/Los_Angeles")
        self.assertTrue(len(scheduled_dict)>0)
        item_id = scheduled_dict[0]["id"]
        self.assertEqual(self.sch1.id, item_id)

    def test_scheduleitems_2_dictB(self):
        all_sch = ScheduleItem.objects.all()
        scheduled_dict = app.service.scheduleitems_2_dict(all_sch, "America/Los_Angeles")
        self.assertTrue(scheduled_dict is not None)


    def test_get_dict_from_meetings_scheduleitems(self):
        items = []
        items += ScheduleItem.objects.all()
        items += Meeting.objects.all()
        all_dict = app.service.get_dict_from_meetings_scheduleitems(items, "America/Los_Angeles")
        self.assertTrue(all_dict is not None)
 
    def test_get_tasks_to_schedule(self):
        selected = app.service.get_tasks_to_schedule(self.user, self.now, "America/Los_Angeles")
        self.assertItemsEqual(selected, [self.todo1, self.todo2, self.todo7])
        self.todo7.done=True
        self.todo7.save()
        selected = app.service.get_tasks_to_schedule(self.user, self.now, "America/Los_Angeles")
        self.assertItemsEqual(selected, [self.todo1, self.todo2])
        self.todo7.done=False
        # you also have to set the when because the done = True above got rid
        # of that
        self.todo7.when='W'
        self.todo7.due=None
        self.todo7.save()
        selected = app.service.get_tasks_to_schedule(self.user, self.now, "America/Los_Angeles")
        self.assertItemsEqual(selected, [self.todo1, self.todo2, self.todo7])

    def test_get_quarters_for_date_with_start(self):
        self.assertEqual(app.service.get_quarters_for_date_with_start(self.anhourago.datetime, self.now), -4)
        self.assertEqual(app.service.get_quarters_for_date_with_start(self.inaminute.datetime, self.now), 1)
        self.assertEqual(app.service.get_quarters_for_date_with_start(self.tomorrow.datetime, self.now), (24*60)/15)
        self.assertEqual(app.service.get_quarters_for_date_with_start(self.yesterday.datetime, self.now), -(24*60)/15)

    def test_get_quarters_from_minutes(self):
        self.assertEqual(app.service.get_quarters_from_minutes(60), 4)
        self.assertEqual(app.service.get_quarters_from_minutes(14), 1)
        self.assertEqual(app.service.get_quarters_from_minutes(76), 6)


    def test_tasks_to_engine(self):
        engine_tasks = app.service.tasks_to_engine([self.todo1, self.todo2, self.todo7], self.now)
        expected = {}
        expected[self.todo1.id] = {"when": 1, "due": 96, "duration": 6}
        expected[self.todo2.id] = {"when": 0, "due": 96}
        expected[self.todo7.id] = {"when": 1, "due": 1}
        self.assertEqual(expected, engine_tasks)

    def test_tasks_to_engine_20140620A(self):
        # duration present?
        task = Task.objects.create(user=self.user, name="testing", done=False, when='T', duration=120)
        engine_tasks = app.service.tasks_to_engine([task], app.service.nearest_quarter_time(self.now))
        self.assertTrue(len(engine_tasks)>0)
        self.assertTrue("duration" in engine_tasks[task.id])
        self.assertEqual(engine_tasks[task.id]["duration"], 8)



    def test_interval_to_from_and_to(self):
        i1 = [0, 3]
        result1 = app.service.interval_to_from_and_to(i1, self.now)
        self.assertEqual(result1[0], self.now)
        inc1 = i1[1]*15
        self.assertEqual(result1[1], self.now.replace(minutes=+inc1))
        i2 = [25, 28]
        result2 = app.service.interval_to_from_and_to(i2, self.now)
        inc2 = i2[0]*15
        self.assertEqual(result2[0], self.now.replace(minutes=+inc2))
        inc3 = i2[1]*15
        self.assertEqual(result2[1], self.now.replace(minutes=+inc3))

    def test_save_scheduleditems_from_engine(self):
        engine_items = {}
        engine_items[self.todo2.id] = [[0, 3], [25, 28]]
        app.service.save_scheduleditems_from_engine(self.user, engine_items, {}, self.now)
        items = ScheduleItem.objects.filter(task=self.todo2)
        self.assertTrue(len(items)==2)
        
    def test_get_arrow_datetime(self):
        pacific = 'America/Los_Angeles'
        morning8 = datetime.time(8,0,0)
        # 0 is Monday
        d1 = app.service.get_arrow_datetime(0, morning8, self.now, pacific, False)
        d1 = app.service.get_arrow_datetime(1, morning8, self.now, pacific, False)
        d1 = app.service.get_arrow_datetime(2, morning8, self.now, pacific, False)
        d1 = app.service.get_arrow_datetime(3, morning8, self.now, pacific, False)
        d1 = app.service.get_arrow_datetime(4, morning8, self.now, pacific, False)
    
    def test_get_arrow_datetime2(self):
        # today is friday and the workweek is just, there is a preference that
        # allows for scheduling on friday
        pacific = 'America/Los_Angeles'
        friday5 = arrow.get('2013-08-16T01:15:00+00:00')
        self.assertEqual(app.service.get_arrow_datetime(4, datetime.time(9,0,0), friday5, pacific, True), arrow.get("2013-08-23T09:00:00-07:00"))
        
        
    def test_nearest_quarter_time(self):
        start = arrow.get('2013-09-29T01:26:43.830580')
        q1 = app.service.nearest_quarter_time(start)
        ex1 = arrow.get('2013-09-29T01:30:00+00:00')
        self.assertEqual(q1, ex1)
        start2 = arrow.get('2013-09-29T01:46:43.830580')
        q2 = app.service.nearest_quarter_time(start2)
        ex2 = arrow.get('2013-09-29T02:00:00+00:00')
        self.assertEqual(q2, ex2)
        
    def test_done_task_should_delete_scheduleitems(self):
        task1 = Task.objects.create(user=self.user, name="task1", done=False)
        task2 = Task.objects.create(user=self.user, name="task2", done=False)
        sch1 = ScheduleItem.objects.create(user=self.user, task=task1, from_date=self.now.datetime, to_date=self.now.datetime)
        sch2 = ScheduleItem.objects.create(user=self.user, task=task1, from_date=self.yesterday.datetime, to_date=self.now.datetime)
        sch3 = ScheduleItem.objects.create(user=self.user, task=task2, from_date=self.yesterday.datetime, to_date=self.now.datetime)
        # different users must stay hidden (despite that the task is the same,
        # which is of course practically impossible)
        sch4 = ScheduleItem.objects.create(user=self.user2, task=task1, from_date=self.yesterday.datetime, to_date=self.now.datetime)

        task1.done=True
        task1.save()
        self.assertFalse(sch1 in ScheduleItem.objects.all())
        self.assertFalse(sch2 in ScheduleItem.objects.all())
        self.assertTrue(sch3 in ScheduleItem.objects.all())
        self.assertTrue(sch4 in ScheduleItem.objects.all())
        
    def test_done_task_should_be_removed_from_comes_after(self):
        task1 = Task.objects.create(user=self.user, name="task1", done=False)
        task2 = Task.objects.create(user=self.user, name="task2", done=False, comes_after=task1)
        task1.save()
        task2.save()

        task1.done=True
        task1.save()

        self.assertFalse(task2 in Task.objects.filter(user=self.user, comes_after=task1))
        self.assertTrue(task2 in Task.objects.filter(user=self.user))
 
    def test_beta_registrations_left(self):
        # first delete all users
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        count1 = User.objects.all().count()
        count2 = UserProfile.objects.all().count()
        self.assertEqual(count1, 0)
        self.assertEqual(count2, 0)

        # Add 2 beta users
        self.user1 = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('paul', 'paul@thebeatles.com', 'johnpassword')
        self.userprofile1 = UserProfile.objects.create(user=self.user1, usertype=0, timezone="America/Los_Angeles")
        self.userprofile2 = UserProfile.objects.create(user=self.user2, usertype=0, timezone="America/Los_Angeles")
        self.userprofile1.save()
        self.userprofile2.save()

        # 50 - beta users + 1 (for admin normally)
        self.assertEqual(app.parameters.TOTAL_ALLOWED_BETA_USERS - 1, app.service.beta_registrations_left())

        # Now remove one
        self.userprofile2.delete()
        self.user2.delete()
        self.assertEqual(app.parameters.TOTAL_ALLOWED_BETA_USERS, app.service.beta_registrations_left())

        # Get rid of added stuff
        self.user1.delete()
        self.userprofile1.delete()


    def test_trial_registrations_left(self):
        # first delete all users
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        count1 = User.objects.all().count()
        count2 = UserProfile.objects.all().count()
        self.assertEqual(count1, 0)
        self.assertEqual(count2, 0)

        # Add 2 trial users
        self.user1 = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('paul', 'paul@thebeatles.com', 'johnpassword')
        self.userprofile1 = UserProfile.objects.create(user=self.user1, usertype=1, timezone="America/Los_Angeles")
        self.userprofile2 = UserProfile.objects.create(user=self.user2, usertype=1, timezone="America/Los_Angeles")
        self.userprofile1.save()
        self.userprofile2.save()

        self.assertEqual(app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 2, app.service.trial_registrations_left())

         # Now remove one
        self.userprofile2.delete()
        self.user2.delete()
        self.assertEqual(app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 1, app.service.trial_registrations_left())

        # Get rid of added stuff
        self.user1.delete()
        self.userprofile1.delete()

    def test_trial_registrations_left_with_users_joined_long_ago(self):
        # first delete all users
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        count1 = User.objects.all().count()
        count2 = UserProfile.objects.all().count()
        self.assertEqual(count1, 0)
        self.assertEqual(count2, 0)

        # Add 2 trial users
        self.user1 = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('paul', 'paul@thebeatles.com', 'johnpassword')
        self.userprofile1 = UserProfile.objects.create(user=self.user1, usertype=1, timezone="America/Los_Angeles")
        self.userprofile2 = UserProfile.objects.create(user=self.user2, usertype=1, timezone="America/Los_Angeles")
        # make sure they joined longer than 32 days ago (which is what
        # trial_registrations_left checks)
        daysago = arrow.utcnow().to(self.userprofile1.timezone.zone).replace(days=-33)
        self.user1.date_joined = daysago.datetime
        self.user2.date_joined = daysago.datetime
        self.user1.save()
        self.user2.save()
        self.userprofile1.save()
        self.userprofile2.save()

        # so the users have no influence on the amount of trial users
        self.assertEqual(app.parameters.TOTAL_ALLOWED_TRIAL_USERS, app.service.trial_registrations_left())

        self.user1.delete()
        self.userprofile1.delete()
        self.user2.delete()
        self.userprofile2.delete()

    def test_speed_trial_registrations_left(self):
        # we test the speed of trial_registrations_left()
        # If you force the evaluate_Trial check namely, this is way too slow.
        # Since trial_registrations_left() is on the front page it always needs
        # to be fast.
        # set amount of trial users to something handleable
        app.parameters.TOTAL_ALLOWED_TRIAL_USERS = 100
        # now create this amount of trial users:
        for i in range(app.parameters.TOTAL_ALLOWED_TRIAL_USERS):
            user = User.objects.create_user(str(i), str(i), str(i))
            UserProfile.objects.create(user=user, usertype=1, timezone="America/Los_Angeles")
        ti = Timer()
        with ti:
            app.service.trial_registrations_left()
        self.assertLess(ti.secs, 0.1)

        # delete all those users again
        User.objects.all().delete()
        UserProfile.objects.all().delete()
    

    def test_trial_registrations_left_mixed1(self):
        # we have 50 places
        app.parameters.TOTAL_ALLOWED_TRIAL_USERS = 50

        # 20 people sign up
        for i in range(20):
            user = User.objects.create_user(str(i), str(i), str(i))
            UserProfile.objects.create(user=user, usertype=1, timezone="America/Los_Angeles")

        # now 30 trials left
        self.assertEqual(app.service.trial_registrations_left(), app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 20)
    
        # 5 go stale
        for i in range(5):
            user = User.objects.get(username=str(i))
            user.date_joined = arrow.utcnow().replace(days=-35).datetime
            user.save()

        # now 5 more trials
        self.assertEqual(app.service.trial_registrations_left(), app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 20 + 5)

        # 4 go pro
        for i in range(7, 11):
            user = User.objects.get(username=str(i))
            user.userprofile.go_pro()

        # this should bring trials up
        self.assertEqual(app.service.trial_registrations_left(), app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 20 + 5 + 4)

        # 6 go undecided
        for i in range(14, 20):
            user = User.objects.get(username=str(i))
            user.userprofile.go_undecided()

        # now 6 more again
        self.assertEqual(app.service.trial_registrations_left(), app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 20 + 5 + 4 + 6)

        # delete all those users again
        User.objects.all().delete()
        UserProfile.objects.all().delete()


    def test_get_meetings_to_schedule(self):
        meetings = app.service.get_meetings_to_schedule(self.user, self.now, "America/Los_Angeles")
        self.assertTrue(meetings is not None)

    def test_get_future_scheduleitems(self):
        items = app.service.get_future_scheduleitems(self.user)
        self.assertTrue(items is not None)

    def test_tasks_to_engine(self):
        tasks = app.service.tasks_to_engine(Task.objects.all(), self.now)
        self.assertTrue(tasks is not None)

    def test_meetings_to_engine(self):
        meetings = app.service.meetings_to_engine(Meeting.objects.all(), self.now)
        self.assertTrue(meetings is not None)

    def test_preferences_to_engine(self):
        meetings = app.service.meetings_to_engine(Meeting.objects.all(), self.now)
        preferences = app.service.preferences_to_engine(self.user, self.now, meetings, "America/Los_Angeles") 

    def test_schedule(self):
        sched = app.service.schedule(self.user, "America/Los_Angeles")
        self.assertTrue(sched is not None)

    def test_create_default_preferences(self):
        app.service.create_default_preferences(self.user)
        self.assertTrue(Preference.objects.filter(user=self.user).exists())

    def test_get_current_and_next_up_in_schedule(self):
        result = app.service.get_current_and_next_up_in_schedule(self.user) 
        self.assertTrue(result is not None)

    def test_trial_registrations_left(self):
        orig = app.parameters.TOTAL_ALLOWED_TRIAL_USERS
        app.parameters.TOTAL_ALLOWED_TRIAL_USERS = 1
        # 2 trial users however
        self.userprofile.usertype = 1
        self.userprofile2.usertype = 1
        self.userprofile.save()
        self.userprofile2.save()
        left = app.service.trial_registrations_left()
        self.assertEqual(0, left)
        app.parameters.TOTAL_ALLOWED_TRIAL_USERS = orig

    def test_beta_registrations_left(self):
        orig = app.parameters.TOTAL_ALLOWED_BETA_USERS
        app.parameters.TOTAL_ALLOWED_BETA_USERS = 1
        # 2 trial users however
        self.userprofile.usertype = 0
        self.userprofile.usertype = 0
        self.userprofile.save()
        self.userprofile2.save()
        left = app.service.beta_registrations_left()
        self.assertEqual(0, left)
        app.parameters.TOTAL_ALLOWED_BETA_USERS = orig

    def test_work_week_over(self):
        # no need to save anything; we'll work on the lists itself
        user = User.objects.create_user('john_work_week', 'lennon_work_week@thebeatles.com', 'johnpassword')
        userprofile = UserProfile.objects.create(user=user, timezone="America/Los_Angeles")

        # Monday
        pref1 = Preference.objects.create(user=user, day=0, from_time="09:00", to_time="17:00")
        pref1.save()
        # Tuesday
        pref2 = Preference.objects.create(user=user, day=1, from_time="09:00", to_time="17:00")
        pref2.save()
        
        prefs = Preference.objects.filter(user=user)

        # Now pretend it is Saturday. So the workweek is clearly over.
        start_arrow = arrow.get('2014-08-16T14:45:00+00:00')
        self.assertTrue(app.service.work_week_over(start_arrow, prefs, "America/Los_Angeles"))

        # Now pretend it is Monday (after hours). Work week is not over.
        start_arrow = arrow.get('2014-08-12T02:45:00+00:00')
        self.assertFalse(app.service.work_week_over(start_arrow, prefs, "America/Los_Angeles"))

        # Now pretend it is Tuesday (after hours). Work week is over.
        start_arrow = arrow.get('2014-08-13T02:45:00+00:00')
        self.assertTrue(app.service.work_week_over(start_arrow, prefs, "America/Los_Angeles"))

        # Now pretend it is Tuesday (in hours). Work week is not over.
        start_arrow = arrow.get('2014-08-12T16:45:00+00:00')
        self.assertFalse(app.service.work_week_over(start_arrow, prefs, "America/Los_Angeles"))
        
        # Now pretend it is Tuesday (on the hour work runs out, 17:01). Work week is over.
        start_arrow = arrow.get('2014-08-13T00:01:00+00:00')
        self.assertTrue(app.service.work_week_over(start_arrow, prefs, "America/Los_Angeles"))

        # clean up
        pref1.delete()
        pref2.delete()


