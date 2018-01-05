import os
BASE_DIR = "/tmp"
SECRET_KEY = 'OC6AMyuklltnlPZbCagbpB2P+'
INSTALLED_APPS = ['portal.plugins.gnmdownloadablelink',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'djcelery',
                  'compressor',
                  'south']

ROOT_URLCONF = 'portal.plugins.gnmdownloadablelink.urls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'djangotestdb.sqlite3'),
    }
}

COMPRESS_URL = '/static/compress/'
VIDISPINE_URL="http://localhost"
VIDISPINE_PORT=8080
VIDISPINE_USERNAME="fakeuser"
VIDISPINE_PASSWORD="fakepassword"

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

DOWNLOADABLE_URL_CHECKINTERVAL = 5
DOWNLOADABLE_LINK_BUCKET = 'fake_bucket'
AWS_REGION = 'eu-west-1'
AWS_ACCESS_KEY_ID = 'fake_key'
AWS_SECRET_ACCESS_KEY = 'fake_secret'