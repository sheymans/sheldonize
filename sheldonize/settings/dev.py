from sheldonize.settings.common import *

# Email settings for development
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'NO'
EMAIL_HOST_PASSWORD = 'NO'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# for password resets this email is used:
DEFAULT_FROM_EMAIL = 'NO'


DEBUG = True
TEMPLATE_DEBUG = True
CONN_MAX_AGE=0
# No chaching of templates in local version
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
         'django.template.loaders.app_directories.Loader')

DATABASES = {
 'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'sheldonizelocaldb',
    'USER': 'root',
    'PASSWORD': 'NONONO',
    'HOST': 'localhost',
    'PORT': '',
 }
}

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = ()
TEMPLATE_DIRS = ()

# Redefine logging for local
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
            'filename': 'app.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'app': {
            'handlers': ['file'],
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

    }
}


# For emailing
ALLOWED_HOSTS = ['*']

# switch off SSL specifics for the local site

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# We add coverage testing to local settings:
# Difference with global one: coverage,
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'django_tables2',
    'crispy_forms',
    'fm', # django-fm for ajax forms
    'timezone_field',
    'braces',
    'coverage',
    # my own:
    'engine',
    'users',
    'subscriptions',
    'app',
    # we put admin after our own apps (as the templates for reset etc should
    # take our own)
    'django.contrib.admin',
    # for profiling
    'debug_toolbar',
    # for python-social-auth,
    'social.apps.django_app.default',
    # for django-watson
    'watson',
)


## STRIPE in development: always uses test keys.
STRIPE_TEST_SECRET_KEY='NO'
STRIPE_TEST_PUBLIC_KEY='NO'
STRIPE_SECRET_KEY=STRIPE_TEST_SECRET_KEY
STRIPE_PUBLIC_KEY=STRIPE_TEST_PUBLIC_KEY


## Google Authentication
GOOGLE_CLIENT_ID='NO'
GOOGLE_CLIENT_SECRET='NO'
GOOGLE_SCOPE='https://www.googleapis.com/auth/calendar.readonly'
GOOGLE_REDIRECT_URI='NO'


## Twitter Login Authentication
SOCIAL_AUTH_TWITTER_SECRET = "NO"
SOCIAL_AUTH_TWITTER_KEY = "NO"


## Google Login Authentication
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "NO"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "NO"


# for error running tests
SOUTH_TESTS_MIGRATE = False
