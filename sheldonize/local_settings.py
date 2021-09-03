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
    'PASSWORD': 'NO',
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
)


## STRIPE in development: always uses test keys.
STRIPE_TEST_SECRET_KEY='NO'
STRIPE_TEST_PUBLIC_KEY='NO'
STRIPE_SECRET_KEY=STRIPE_TEST_SECRET_KEY
STRIPE_PUBLIC_KEY=STRIPE_TEST_PUBLIC_KEY

