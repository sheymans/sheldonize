from selenium import webdriver
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from users.models import UserProfile
from app.models import Task
import utils
import app.service

class GetHelpTest(LiveServerTestCase):

  def setUp(self):
      self.browser = webdriver.Firefox()

  def tearDown(self):
      self.browser.quit()

  def test_gethelp(self):    
      # When user click on get help, he can add a task for the 'support' user.

      # first create user
      u = User.objects.create_user('test', 'test@test.com', 'testpassword')
      UserProfile.objects.create(user=u, usertype=0, timezone="America/Los_Angeles")

      # Login that user via browser
      utils.login(self.browser, self, u, 'testpassword')

      # Check that he is indeed logged in
      self.assertIn('Tasks', self.browser.title)

      self.browser.get(self.live_server_url + '/app/support/')
      inputname = self.browser.find_element_by_id('id_name')
      inputname.send_keys("please help us support")
      # not just submit() cause the button sends new_task in form (which submit
      # does not do)
      self.browser.find_element_by_name("new_task").click()
      self.browser.implicitly_wait(10)

      # Now check whether the support account contains that item:
      support = User.objects.get(username='support')
      tasks = Task.objects.filter(user=support)
      self.assertTrue(len(tasks) == 1)
      self.assertEqual(tasks[0].name, "please help us support")
       

      # Finally, Get rid of added users:
      User.objects.all().delete()
      UserProfile.objects.all().delete()
      # And get rid of tasks
      Task.objects.all().delete()

