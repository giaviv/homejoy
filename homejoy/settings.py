
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'okk1w(!0^mj4yye@d9f&lp!t#y%j4k4^scvayazo*w^jg@bdr!'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'zipcoder',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'homejoy.urls'

WSGI_APPLICATION = 'homejoy.wsgi.application'

DATABASES = {}
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATIC_URL = '/static/'

GOOGLE_API_KEY = 'AIzaSyDViIUJoD1PM2FXGESw6PrRzBvV3oQ6--0'

DATA_DIR = os.path.join(BASE_DIR, 'data2')

ZIPCODES_SHP = os.path.join(DATA_DIR, 'cb_2013_us_zcta510_500k.shp')

RTREE_INDEX_FILE = os.path.join(DATA_DIR, 'rtree')

RTREE_INDEX_FILE_NAME = RTREE_INDEX_FILE + '.dat'

TMP_DIR = os.path.join(BASE_DIR, 'tmp')


