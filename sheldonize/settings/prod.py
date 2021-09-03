from sheldonize.settings.common import *


# Email settings for production
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@sheldonize.com'
EMAIL_HOST_PASSWORD = 'NO'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# for password resets this email is used:
DEFAULT_FROM_EMAIL = 'NO'



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['sheldonize.com', 'www.sheldonize.com', '54.183.182.162' ]


## ALLOWED_HOST Issue (ELB health check change post headers to internal IP so sheldonize.com does not get recognized anymore)
## http://dryan.me/articles/elb-django-allowed-hosts/

import requests
EC2_PRIVATE_IP = None
try:
    EC2_PRIVATE_IP = requests.get('http://NO/latest/meta-data/local-ipv4', timeout = 0.01).text
except requests.exceptions.RequestException:
    pass

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)

# When Debug = False, 500 error will be send to ADMINS
ADMINS = (
    ('Admin', 'admin@sheldonize.com'),
)

# Database related: allow for connections to persist for x seconds (default is
# 0, no persistence -- opening connections takes time so DB intensive
# applications can benefit from this).
CONN_MAX_AGE=300


# When Debug = False, 404 error will be send to MANAGERS
MANAGERS = (
    ('Admin', 'admin@sheldonize.com'),
)

# HTTPS Stuff (to ensure when the HTTP_X_FORWARDED_PROTO header is present
# sheldonize treats this as HTTPS) -- see
# http://rickchristianson.wordpress.com/2013/10/31/getting-a-django-app-to-use-https-on-aws-elastic-beanstalk/

#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Chached template loader (when first encountering them it caches -- speed up):
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'django_tables2',
    'crispy_forms',
    'fm',
    'timezone_field',
    'braces',
    # my own:
    'engine',
    'users',
    'subscriptions',
    'app',
    # we put admin after our own apps (as the templates for reset etc should
    # take our own)
    'django.contrib.admin',
    # for python-social-auth,
    'social.apps.django_app.default',
    # for django-watson
    'watson',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ebdb',
        'USER' : 'ebroot',
        'PASSWORD' : 'NONO',
        'HOST' : 'sheldyawsdb.NO.us-west-1.rds.amazonaws.com',
        'PORT' : '3306',
    }
}


# Logging

# see
# http://ianalexandr.com/blog/getting-started-with-django-logging-in-5-minutes.html

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
                },
            },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/home/ubuntu/webapps/sheldonize/logs/sheldonize.log',
                'formatter': 'verbose'
                },
            },
        'loggers': {
            'app': {
                'handlers': ['file'], # use mail_admin instead of file if you want to send email (see also above, EMAIL_HOST etc)
                'level': 'ERROR',
                },
            'subscriptions': {
                'handlers': ['file'],
                'level': 'ERROR',
                },
            'users': {
                'handlers': ['file'],
                'level': 'ERROR',
                },
            },
        }

## STRIPE BASE SETTINGS: don't change unless api keys at stripe.com change
# Do not use these directly in code either. Use the ones without TEST or LIVE
# instead below.
STRIPE_TEST_SECRET_KEY='NO'
STRIPE_TEST_PUBLIC_KEY='NO'
STRIPE_LIVE_SECRET_KEY='NO'
STRIPE_LIVE_PUBLIC_KEY='NO'

## Set here what we are using, for now both in production and development we use TEST keys
## LIVE KEYS ARE ARMED! Note that we override that in local_settings to avoid mayhem when testing.
STRIPE_SECRET_KEY=STRIPE_LIVE_SECRET_KEY
STRIPE_PUBLIC_KEY=STRIPE_LIVE_PUBLIC_KEY



# The S3 Bucket
INSTALLED_APPS += ('storages',)
AWS_STORAGE_BUCKET_NAME = "sheldy-s3-us-west-1"
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL

## Google Authentication for downloading of Calendar
GOOGLE_CLIENT_ID='NO'
GOOGLE_CLIENT_SECRET='NO'
GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar.readonly'
GOOGLE_REDIRECT_URI='https://sheldonize.com/app/oauth2callback'


## Twitter Login Authentication
SOCIAL_AUTH_TWITTER_SECRET = "NO"
SOCIAL_AUTH_TWITTER_KEY = "NO"

## Google Login Authentication
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "NO"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "NO"
