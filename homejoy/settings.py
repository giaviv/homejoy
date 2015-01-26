
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'okk1w(!0^mj4yye@d9f&lp!t#y%j4k4^scvayazo*w^jg@bdr!'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles' # West coast best coast

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATIC_URL = '/static/'
# my key for the Google API services
GOOGLE_API_KEY = 'AIzaSyDViIUJoD1PM2FXGESw6PrRzBvV3oQ6--0'
# the directory where the zipcode shape data lie as well as the rtree index
DATA_DIR = os.path.join(BASE_DIR, 'data')
# file name for the zipcode shp file
ZIPCODES_SHP = os.path.join(DATA_DIR, 'cb_2013_us_zcta510_500k.shp')
# rtree index file
RTREE_INDEX_FILE = os.path.join(DATA_DIR, 'rtree')
# physical rtree index filename
RTREE_INDEX_FILE_NAME = RTREE_INDEX_FILE + '.dat'
# temp directory to store route shapes used for calculations
TMP_DIR = os.path.join(BASE_DIR, 'tmp')


