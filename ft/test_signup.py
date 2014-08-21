from selenium import webdriver
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.common.exceptions import NoSuchElementException
import app.parameters

import time

from users.models import UserProfile
import app.service

class SignUpTest(LiveServerTestCase):

  def setUp(self):
      self.browser = webdriver.Firefox()


  def tearDown(self):
      self.browser.quit()

  def test_signup_very_longemail(self):
      # email longer than allowed username; this test should make sure that
      # username is properly separated from email

      self.browser.get(self.live_server_url + '/users/signup/')

      inputusername = self.browser.find_element_by_id('id_username')
      inputemail = self.browser.find_element_by_id('id_email')
      inputpassword = self.browser.find_element_by_id('id_password')
        
    # Type in the too long username, and password
      inputusername.send_keys('wilfred_longemail')
      inputemail.send_keys('wilfred11111111111111111111111111111111111111111111111111111@gmail.com')
      inputpassword.send_keys('yupup')

      # verify that this goes fine:
      inputemail.submit()
      self.assertIn('Tasks', self.browser.title)


  def test_signup_when_limit_trial_users_has_been_reached(self):    
      # set the total allowed trial users to something smaller for testing
      app.parameters.TOTAL_ALLOWED_TRIAL_USERS = 50

      # Some setup (add users to fill up trial registrations)
      for i in range(app.parameters.TOTAL_ALLOWED_TRIAL_USERS):
          u = User.objects.create_user(str(i), str(i), str(i))
          # Usertype 1 is TRIAL
          UserProfile.objects.create(user=u, usertype=1, timezone="America/Los_Angeles")
      # Check that they are indeed added
      self.assertEqual(UserProfile.objects.all().count(), app.parameters.TOTAL_ALLOWED_TRIAL_USERS)

      # sign up should fail when limit of trial users has been reached
      self.browser.get(self.live_server_url + '/users/signup/')

      # We are indeed on the signup page:
      self.assertIn('Sign Up', self.browser.title)

      # Get the input boxes for email and password and timezone:
      inputusername = self.browser.find_element_by_id('id_username')
      inputemail = self.browser.find_element_by_id('id_email')
      inputpassword = self.browser.find_element_by_id('id_password')
      inputtimezone = self.browser.find_element_by_id('id_timezone')

      # Type in the email, and password
      inputusername.send_keys('wilfred')
      inputemail.send_keys('wilfred@gmail.com')
      inputpassword.send_keys('yupup')

      # Submit can be send to any element within a form (according to Selenium)
      inputemail.submit()
    
      # Now make sure there is an error
      try:
          error_msg = self.browser.find_element_by_css_selector('span.help-block > strong')
      except NoSuchElementException:
          self.fail('Could not find expected error')

      self.assertIn('We have reached the maximum of trial users we allow', error_msg.text)

      # Now remove a user and confirm that there is then place again.
      u = User.objects.get(email=str(5))
      p = u.userprofile
      p.delete()
      u.delete()
      self.assertEqual(UserProfile.objects.all().count(), app.parameters.TOTAL_ALLOWED_TRIAL_USERS - 1)
      # email field is still filled in but needs to get refreshed from page
      inputusername = self.browser.find_element_by_id('id_username')
      inputemail = self.browser.find_element_by_id('id_email')
      inputpassword = self.browser.find_element_by_id('id_password')
      inputpassword.send_keys('yupup')
      inputemail.submit()
      self.assertIn('Tasks', self.browser.title)


      # Finally, Get rid of added users:
      User.objects.all().delete()
      UserProfile.objects.all().delete()

