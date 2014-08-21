from selenium import webdriver
from django.test import LiveServerTestCase
from django.contrib.auth.models import User

class TasksTest(LiveServerTestCase):

  def setUp(self):
      self.browser = webdriver.Firefox()
      self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')


  def tearDown(self):
      self.browser.quit()

  def test_tasks_title(self):    
      # no login
      self.browser.get(self.live_server_url + '/app/tasks/')
      self.assertIn('Sign In', self.browser.title)
