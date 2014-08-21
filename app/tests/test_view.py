from django.test import TestCase, Client
from django.core.urlresolvers import resolve
from app.views import tasks, schedule
from app.models import Task, Preference, Meeting, ScheduleItem
import app.parameters
from users.models import UserProfile
from django.contrib.auth.models import User

import arrow

class ViewTest(TestCase):
    def setUp(self):
        self.client_stub = Client()
        self.user = User.objects.create_user('lennon', 'lennon@thebeatles.com', 'johnpassword')
        self.user2 = User.objects.create_user('paul', 'paul@thebeatles.com', 'paulpassword')
        self.userprofile = UserProfile.objects.create(user=self.user, usertype=0, timezone="America/Los_Angeles")
        # paul is a trial user
        self.userprofile2 = UserProfile.objects.create(user=self.user2, timezone="America/Los_Angeles", usertype=1)

        self.task1 = Task.objects.create(user=self.user, name='task 1', done=False) 
        self.task2 = Task.objects.create(user=self.user, name='task 2', done=False) 
        self.task3 = Task.objects.create(user=self.user, name='task 3', done=False) 
        self.task_paul = Task.objects.create(user=self.user2, name='task paul', done=False) 
        self.task1.save()
        self.task2.save()
        self.task3.save()

        self.preference1 = Preference.objects.create(user=self.user, day=0, from_time="09:00", to_time="17:00")
        self.preference_paul = Preference.objects.create(user=self.user2, day=0, from_time="09:00", to_time="17:00")
        self.preference1.save()
        self.preference_paul.save()


        self.meeting1 = Meeting.objects.create(user=self.user, name="Meeting 1", start="2014-08-11 11:00:00-07:00", end="2014-08-11 11:00:00-07:00")
        self.meeting2 = Meeting.objects.create(user=self.user, name="Meeting 2", start="2014-08-11 11:00:00-07:00", end="2014-08-11 11:00:00-07:00")
        self.meeting_paul = Meeting.objects.create(user=self.user2, name="Meeting Paul", start="2014-08-11 11:00:00-07:00", end="2014-08-11 11:00:00-07:00")
        self.meeting1.save()
        self.meeting2.save()
        self.meeting_paul.save()

        self.scheduleitem = ScheduleItem.objects.create(user=self.user, task=self.task1, from_date="2014-08-11 11:00:00-07:00", to_date="2014-08-11 12:00:00-07:00")
        self.scheduleitem.save()


    def tearDown(self):
        self.userprofile.delete()
        self.user.delete()
        self.task1.delete()
        self.task2.delete()
        self.task3.delete()
        self.task_paul.delete()
        self.meeting1.delete()
        self.meeting2.delete()
        self.meeting_paul.delete()
        self.scheduleitem.delete()


    def test_url_tasks_resolves_to_function(self):
        # figure out that app/tasks relays to the tasks function in the views
        found = resolve('/app/tasks/')
        self.assertEquals(found.func, tasks)

    def test_basic_sanity_tasks(self):
        task1 = Task.objects.create(user=self.user, name="random", done=False)
        task1.save()
        response = self.client_stub.post('/users/login/', {'username': 'lennon', 'password': 'johnpassword'})
        response = self.client_stub.get('/app/tasks/')
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'Apply', response.content)

    def test_eventfeed_incomplete(self):
        response = self.client_stub.get('/app/schedule/incomplete/')


    def test_trial_registrations_left(self):
        # get the main page
        self.client_stub.logout()
        response = self.client_stub.get("/app/")
        # -1 for the trial user paul
        self.assertEqual(response.context['trial_registrations_left'], app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 1)

    def test_home_with_user_authenticated(self):
        # if a logged in person goes to the home page, he should be directed to
        # /app/tasks
        # pretend anyone is logged in
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/', follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/app/tasks/', 302)])
        
    def test_healthcheck(self):
        # Should just return OK (200)
        response = self.client_stub.get('/healthcheck/')
        self.assertEqual(response.status_code, 200)
       
    def test_terms_of_use(self):
        response = self.client_stub.get('/app/terms/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'terms_of_use.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_privacy(self):
        response = self.client_stub.get('/app/privacy/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'privacy.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_get_support_not_logged_in(self):
        # not logged in
        response = self.client_stub.get('/app/support/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('http://testserver/users/login/?next=/app/support/', 302)])

    def test_get_support_logged_in(self):
        # to get support you have to logged in
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/support/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) > 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'support.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_post_new_task_get_support(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/support/', {'name': 'support question', 'new_task': ''})
        self.assertEqual(response.status_code, 302)
        # Check that after such a post the support account indeed exists
        self.assertTrue(User.objects.filter(username='support'))
        # check that the support account indeed has that task  in its list
        support = User.objects.get(username='support')
        self.assertTrue(Task.objects.filter(user=support, name='support question').exists())

    def test_post_without_new_task_get_support(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        # new_task is missing, will move through, without doing anything
        response = self.client_stub.post('/app/support/', {'name': 'support question' })
        self.assertEqual(response.status_code, 302)

    def test_post_with_empty_task_get_support(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        # new_task is missing, will move through, without doing anything
        response = self.client_stub.post('/app/support/', {'name': '', 'new_task': '' })
        self.assertEqual(response.status_code, 302)

    def test_put_get_support(self):
        # put should raise a 404
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.put('/app/support/', {'name': 'bla', 'new_task': '' })
        self.assertEqual(response.status_code, 404)

    def test_get_tasks_incomplete(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/incomplete/')
        self.assertEqual(response.status_code, 200)

    def test_get_tasks_incomplete_notnow(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/incomplete/inbox/')
        self.assertEqual(response.status_code, 200)

    def test_get_tasks_incomplete_today(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/incomplete/today/')
        self.assertEqual(response.status_code, 200)

    def test_get_tasks_incomplete_thisweek(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/incomplete/thisweek/')
        self.assertEqual(response.status_code, 200)

    def test_get_tasks_done(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/done/')
        self.assertEqual(response.status_code, 200)

    def test_post_tasks_complete(self):
        id1 = self.task1.id
        id2 = self.task2.id
        # before they are in 'not done'
        self.assertTrue(Task.objects.filter(id=id1, done=False).exists())
        self.assertTrue(Task.objects.filter(id=id2, done=False).exists())
        # mark them as done:
        post_data = { 'selection': [id1, id2], 'complete-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )

        # should now be done
        self.assertTrue(Task.objects.filter(id=id1, done=True).exists())
        self.assertTrue(Task.objects.filter(id=id2, done=True).exists())
        self.assertFalse(Task.objects.filter(id=id1, done=False).exists())
        self.assertFalse(Task.objects.filter(id=id2, done=False).exists())

    def test_post_tasks_complete_20140818(self):
        # we are going to test whether when we mark a task as done, its due
        # date stays te same!
        id1 = self.task1.id
        duedate = arrow.get("2014-08-11 11:00:00-07:00").datetime
        self.task1.due = duedate
        self.task1.save()
        # before they are in 'not done'
        self.assertTrue(Task.objects.filter(id=id1, done=False).exists())
        # and due date is equal to that thing
        self.assertEqual(self.task1.due, duedate)
        # mark it as done:
        post_data = { 'selection': [id1], 'complete-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )

        # should now be done
        self.assertTrue(Task.objects.filter(id=id1, done=True).exists())
        self.assertFalse(Task.objects.filter(id=id1, done=False).exists())
        # and due date is still the same
        # get the task freshly
        t = Task.objects.get(id=id1)
        self.assertEqual(t.due, duedate)
        

    def test_post_tasks_uncomplete(self):
        id1 = self.task1.id
        id2 = self.task2.id
        self.task1.done = True
        self.task2.done = True
        # mark them as not done:
        post_data = { 'selection': [id1, id2], 'uncomplete-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/done/', post_data )

        # should now be not done
        self.assertTrue(Task.objects.filter(id=id1, done=False).exists())
        self.assertTrue(Task.objects.filter(id=id2, done=False).exists())

    def test_post_tasks_delete(self):
        id1 = self.task1.id
        id2 = self.task2.id
        # delete them
        post_data = { 'selection': [id1, id2], 'delete-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/', post_data )

        # should now be deleted
        self.assertFalse(Task.objects.filter(id=id1).exists())
        self.assertFalse(Task.objects.filter(id=id2).exists())

    def test_post_tasks_thisweek_mark(self):
        id1 = self.task1.id
        id2 = self.task2.id
        # They are not marked for this week
        self.assertFalse(Task.objects.filter(id=id1, when='W').exists())
        self.assertFalse(Task.objects.filter(id=id2, when='W').exists())
        # Mark them as this week
        post_data = { 'selection': [id1, id2], 'thisweek-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )

        # should now be done this week
        self.assertTrue(Task.objects.filter(id=id1, when='W').exists())
        self.assertTrue(Task.objects.filter(id=id2, when='W').exists())

    def test_post_tasks_today_mark(self):
        id1 = self.task1.id
        id2 = self.task2.id
        # They are not marked for today
        self.assertFalse(Task.objects.filter(id=id1, when='T').exists())
        self.assertFalse(Task.objects.filter(id=id2, when='T').exists())
        # Mark them as today
        post_data = { 'selection': [id1, id2], 'today-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )

        # should now be done today
        self.assertTrue(Task.objects.filter(id=id1, when='T').exists())
        self.assertTrue(Task.objects.filter(id=id2, when='T').exists())

    def test_post_tasks_nowhen_mark(self):
        id1 = self.task1.id
        id2 = self.task2.id
        # They are not marked for today
        self.assertFalse(Task.objects.filter(id=id1, when='T').exists())
        self.assertFalse(Task.objects.filter(id=id2, when='T').exists())
        # Mark them as today
        post_data = { 'selection': [id1, id2], 'today-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )

        # should now be done today
        self.assertTrue(Task.objects.filter(id=id1, when='T').exists())
        self.assertTrue(Task.objects.filter(id=id2, when='T').exists())

        # And now mark without today
        post_data = { 'selection': [id1, id2], 'nowhen-marked-tasks': '' }
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )
        self.assertTrue(Task.objects.filter(id=id1, when=None).exists())
        self.assertTrue(Task.objects.filter(id=id2, when=None).exists())

    def test_post_new_task_valid_inbox(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': 'some new task', 'new_task': '' }
        response = self.client_stub.post('/app/tasks/incomplete/inbox/', post_data )
        self.assertTrue(Task.objects.filter(name='some new task', when=None).exists())

    def test_post_new_task_valid_today(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': 'some new task', 'new_task': '' }
        response = self.client_stub.post('/app/tasks/incomplete/today/', post_data )
        self.assertTrue(Task.objects.filter(name='some new task', when='T').exists())

    def test_post_new_task_valid_thisweek(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': 'some new task', 'new_task': '' }
        response = self.client_stub.post('/app/tasks/incomplete/thisweek/', post_data )
        self.assertTrue(Task.objects.filter(name='some new task', when='W').exists())

    def test_post_new_task_invalid(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': '', 'new_task': '' }
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )
        self.assertFalse(Task.objects.filter(name='some new task', when=None).exists())

    def test_post_go_to_schedule(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'go-to-schedule': '' }
        response = self.client_stub.post('/app/tasks/incomplete/', post_data, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/app/schedule/', 302)])

    def test_post_tasks_today_withouttaskselection(self):
        # no tasks selected
        post_data = { 'selection': [], 'today-marked-tasks': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/tasks/incomplete/', post_data )

    def test_put_tasks(self):
        # put should raise a 404
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.put('/app/tasks/', {'name': 'bla', 'new_task': '' })
        self.assertEqual(response.status_code, 404)


    def test_get_task_permission_denied(self):
        idpaul = self.task_paul.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/' + str(idpaul) + '/')
        # permission denied
        self.assertEqual(response.status_code, 403)

    def test_get_task(self):
        id1 = self.task1.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/tasks/' + str(id1) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) >= 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'app/task.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_post_delete_task(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        self.assertTrue(Task.objects.filter(id=id1).exists())
        post_data = { 'delete-task': '' }
        response = self.client_stub.post('/app/tasks/' + str(id1) + '/', post_data)
        # now the task is gone:
        self.assertFalse(Task.objects.filter(id=id1).exists())

    def test_post_update_task(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        name = self.task1.name
        self.assertTrue(Task.objects.filter(id=id1, name=name).exists())
        post_data = { 'name': 'new task' }
        response = self.client_stub.post('/app/tasks/' + str(id1) + '/', post_data)
        # now the task is updated:
        self.assertFalse(Task.objects.filter(id=id1, name=name).exists())
        self.assertTrue(Task.objects.filter(id=id1, name='new task').exists())

    def test_post_wrong_update_task(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        name = self.task1.name
        self.assertTrue(Task.objects.filter(id=id1, name=name).exists())
        post_data = { 'name': '' }
        response = self.client_stub.post('/app/tasks/' + str(id1) + '/', post_data)
        # now the task is NOT updated:
        self.assertTrue(Task.objects.filter(id=id1, name=name).exists())
        self.assertFalse(Task.objects.filter(id=id1, name='').exists())

    def test_put_task(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        response = self.client_stub.put('/app/tasks/' + str(id1) + '/', {})
        self.assertEqual(response.status_code, 404)


    def test_get_task_incomplete(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        response = self.client_stub.get('/app/tasks/incomplete/' + str(id1) + "/")
        self.assertEqual(response.status_code, 200)

    def test_get_task_incomplete_inbox(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        response = self.client_stub.get('/app/tasks/incomplete/inbox/' + str(id1) + "/")
        self.assertEqual(response.status_code, 200)

    def test_get_task_incomplete_today(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        response = self.client_stub.get('/app/tasks/incomplete/today/' + str(id1) + "/")
        self.assertEqual(response.status_code, 200)

    def test_get_task_incomplete_thisweek(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        response = self.client_stub.get('/app/tasks/incomplete/thisweek/' + str(id1) + "/")
        self.assertEqual(response.status_code, 200)

    def test_get_task_done(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.task1.id
        response = self.client_stub.get('/app/tasks/done/' + str(id1) + "/")
        self.assertEqual(response.status_code, 200)

    def test_get_schedule_mobile(self):
        # Middleware does NOT detect this I think TODO
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/schedule/', **{'HTTP_USER_AGENT': 'iphone'})
        self.assertEqual(response.status_code, 200)


    def test_post_schedule(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'calculate-schedule': '' }
        response = self.client_stub.post('/app/schedule/', post_data)
        self.assertEqual(response.status_code, 200)

    def test_delete_schedule(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'delete-schedule': '' }
        response = self.client_stub.post('/app/schedule/', post_data)
        self.assertEqual(response.status_code, 200)

    def test_get_eventfeed(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/eventfeed/')
        self.assertEqual(response.status_code, 200)

    def test_post_eventfeed(self):
        # should fail with 404
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/eventfeed/', {})
        self.assertEqual(response.status_code, 404)

    def test_post_delete_preference(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.preference1.id
        self.assertTrue(Preference.objects.filter(id=id1).exists())
        post_data = { 'delete-preference': '' }
        response = self.client_stub.post('/app/preferences/' + str(id1) + '/', post_data)
        # now the preference is gone:
        self.assertFalse(Preference.objects.filter(id=id1).exists())

    def test_post_delete_preference_notallowed(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.preference_paul.id
        self.assertTrue(Preference.objects.filter(id=id1).exists())
        post_data = { 'delete-preference': '' }
        response = self.client_stub.post('/app/preferences/' + str(id1) + '/', post_data)
        # permission denied (not your own preference)
        self.assertEqual(response.status_code, 403)
        # the preference is still there:
        self.assertTrue(Preference.objects.filter(id=id1).exists())

    def test_get_preferences(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/preferences/')
        self.assertEqual(response.status_code, 200)

    def test_post_new_preference_valid(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'day': 1, 'from_time': '9:00 AM', 'to_time': '5:00 PM', 'new_preference': '' }
        response = self.client_stub.post('/app/preferences/', post_data )
        self.assertTrue(Preference.objects.filter(day=1).exists())
        self.assertEqual(response.status_code, 302)

    def test_post_new_preference_invalid(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'day': 10, 'from_time': '9:00 AM', 'to_time': '5:00 PM', 'new_preference': '' }
        response = self.client_stub.post('/app/preferences/', post_data )
        self.assertFalse(Preference.objects.filter(day='10').exists())
        self.assertEqual(response.status_code, 302)

    def test_put_preferences(self):
         # puts fail
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.put('/app/preferences/', {} )
        self.assertEqual(response.status_code, 404)
 
    def test_get_meetings(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/')
        self.assertEqual(response.status_code, 200)

    def test_get_meetings_past(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/past/')
        self.assertEqual(response.status_code, 200)

    def test_get_meetings_future(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/future/')
        self.assertEqual(response.status_code, 200)

    def test_post_meetings_delete(self):
        id1 = self.meeting1.id
        id2 = self.meeting2.id
        self.assertTrue(Meeting.objects.filter(id=id1).exists())
        self.assertTrue(Meeting.objects.filter(id=id2).exists())
        # delete them
        post_data = { 'selection': [id1, id2], 'delete-marked-meetings': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/meetings/', post_data )

        # should now be deleted
        self.assertFalse(Meeting.objects.filter(id=id1).exists())
        self.assertFalse(Meeting.objects.filter(id=id2).exists())

    def test_post_new_meeting_valid(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': 'some new meeting', 'new_meeting': '' }
        response = self.client_stub.post('/app/meetings/', post_data )
        self.assertTrue(Meeting.objects.filter(name='some new meeting').exists())

    def test_post_new_meeting_invalid(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': '', 'new_meeting': '' }
        response = self.client_stub.post('/app/meetings/', post_data )
        self.assertFalse(Meeting.objects.filter(name='some new meeting').exists())

    def test_post_meetings_go_to_schedule(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'go-to-schedule': '' }
        response = self.client_stub.post('/app/meetings/', post_data, follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/app/schedule/', 302)])

    def test_post_meetings_withouttaskselection(self):
        # no meetings selected
        post_data = { 'selection': [], 'delete-marked-meetings': '' }
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.post('/app/meetings/', post_data )

    def test_put_meetings(self):
        # put should raise a 404
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.put('/app/meetings/', {'name': 'bla', 'new_meeting': '' })
        self.assertEqual(response.status_code, 404)

    def test_get_meeting_permission_denied(self):
        idpaul = self.meeting_paul.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/' + str(idpaul) + '/')
        # permission denied
        self.assertEqual(response.status_code, 403)

    def test_get_meeting(self):
        id1 = self.meeting1.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/' + str(id1) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) >= 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'app/meeting.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_post_delete_meeting(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.meeting1.id
        self.assertTrue(Meeting.objects.filter(id=id1).exists())
        post_data = { 'delete-meeting': '' }
        response = self.client_stub.post('/app/meetings/' + str(id1) + '/', post_data)
        # now the meeting is gone:
        self.assertFalse(Meeting.objects.filter(id=id1).exists())

    def test_post_update_meeting(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.meeting1.id
        name = self.meeting1.name
        self.assertTrue(Meeting.objects.filter(id=id1, name=name).exists())
        post_data = { 'name': 'new meeting', 'start': '08/11/2014 11:00 am', 'end': '08/11/2014 12:00 pm'}
        response = self.client_stub.post('/app/meetings/' + str(id1) + '/', post_data)
        # now the meeting is updated:
        self.assertFalse(Meeting.objects.filter(id=id1, name=name).exists())
        self.assertTrue(Meeting.objects.filter(id=id1, name='new meeting').exists())

    def test_post_wrong_update_meeting(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.meeting1.id
        name = self.meeting1.name
        self.assertTrue(Meeting.objects.filter(id=id1, name=name).exists())
        post_data = { 'name': '', 'start': '08/11/2014 11:00 am', 'end': '08/11/2014 12:00 pm'}
        response = self.client_stub.post('/app/meetings/' + str(id1) + '/', post_data)
        # now the meeting is NOT updated:
        self.assertTrue(Meeting.objects.filter(id=id1, name=name).exists())
        self.assertFalse(Meeting.objects.filter(id=id1, name='').exists())

    def test_put_meeting(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        id1 = self.meeting1.id
        response = self.client_stub.put('/app/meetings/' + str(id1) + '/', {})
        self.assertEqual(response.status_code, 404)

    def test_get_past_meeting(self):
        # doesn't matter whether this meeting is in past, we want to check
        # /past url
        id1 = self.meeting1.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/past/' + str(id1) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) >= 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'app/meeting.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_get_future_meeting(self):
        # doesn't matter whether this meeting is in future, we want to check
        # /past url
        id1 = self.meeting1.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/meetings/future/' + str(id1) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.templates) >= 2)
        first_template = response.templates[0]
        second_template = response.templates[1]
        self.assertEqual(first_template.name, 'app/meeting.html')
        self.assertEqual(second_template.name, 'base.html')

    def test_post_ajax_meeting(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'name': 'new meeting', 'start': '2014-08-11 11:00:00-07:00', 'end': '2014-08-11 12:00:00-07:00'}
        response = self.client_stub.post('/app/meetings/ajax/', post_data)
        self.assertTrue(Meeting.objects.filter(name='new meeting').exists())

    def test_post_ajax_meeting_with_id(self):
        id1 = self.meeting1.id
        self.client_stub.login(username='lennon', password='johnpassword')
        post_data = { 'id': id1, 'name': 'new meeting', 'start': '2014-08-11 11:00:00-07:00', 'end': '2014-08-11 13:00:00-07:00'}
        response = self.client_stub.post('/app/meetings/ajax/', post_data)
        self.assertTrue(Meeting.objects.filter(id=id1, end = '2014-08-11 13:00:00-07:00').exists())

    def test_ajax_meeeting_invalid(self):
        self.client_stub.login(username='lennon', password='johnpassword')
        # gets are not allowed on ajax meetings
        response = self.client_stub.get('/app/meetings/ajax/')
        self.assertEqual(response.status_code, 404)

    def test_get_scheduleitem(self):
        id1 = self.scheduleitem.id
        self.client_stub.login(username='lennon', password='johnpassword')
        response = self.client_stub.get('/app/scheduleitems/' + str(id1) + '/', follow=True)
        self.assertEqual(response.redirect_chain, [('http://testserver/app/tasks/' + str(self.scheduleitem.task.id) + '/', 302)])
