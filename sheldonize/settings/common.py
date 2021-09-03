"""
Django settings for sheldonize project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import django.conf.global_settings as DEFAULT_SETTINGS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'NOOONONONO'

# what is the default login page
LOGIN_URL='/users/login/'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # we're switching to modals so no messing around anymore with previousURL
    # 'sheldonize.middleware.PreviousURLMiddleware',
    'sheldonize.middleware.DetectMobile',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sheldonize.urls'

WSGI_APPLICATION = 'sheldonize.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# as requested by amazon django tutorial
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')


# for django-tables2
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
        'social.apps.django_app.context_processors.backends',
        'social.apps.django_app.context_processors.login_redirect',
        )

# for cripsy-forms (let's go for bootstrap3)
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Message tags
# http://ericsaupe.com/tag/bootstrap-messages-fix/
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger',}


AUTHENTICATION_BACKENDS = (
          #'social.backends.open_id.OpenIdAuth',
          #'social.backends.google.GoogleOpenId',
          'social.backends.google.GoogleOAuth2',
          #'social.backends.google.GoogleOAuth',
          'social.backends.twitter.TwitterOAuth',
          #'social.backends.yahoo.YahooOpenId',
          'django.contrib.auth.backends.ModelBackend',
)

# Where we redirect after authorizing another application:
LOGIN_REDIRECT_URL='/app/tasks/'

# we're overriding the social pipeline by creating the user profile (similar as
# in signup)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    # this associates the new social login by email with an existing account.
    # You need to make sure that all social login providers verify that the
    # email belongs to these users otherwise malicious users could attach to
    # your account.
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    # here we'll create user profile as in signup
    'users.socialsignup.create_userprofile',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)


# For django ajax forms
FM_DEFAULT_FORM_TEMPLATE = "app/modal_form.html"
