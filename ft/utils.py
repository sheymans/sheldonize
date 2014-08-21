# Some utils for the functional tests


# Log in a user

def login(browser, liveservertestcase, user, password):
      browser.get(liveservertestcase.live_server_url + '/users/login/')

      # Get the input boxes for email and password and timezone:
      inputusername = browser.find_element_by_id('username')
      inputpassword = browser.find_element_by_id('password')

      inputusername.send_keys(user.username)
      inputpassword.send_keys(password)

      inputusername.submit()

      # We should now be logged in
