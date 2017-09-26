import os
import logging
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

BASE_DIR = "/tmp"
SECRET_KEY = 'n0555U1UAiKI/LsKYL1MqcRltPo9BRDkAGuX+Ww'
INSTALLED_APPS = ['portal.plugins.kinesisresponder',
                  'south',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions'
                  ]

ROOT_URLCONF = 'portal.plugins.kinesisresponder.urls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'krestestdb.sqlite3'),
    }
}

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

VIDISPINE_URL="http://localhost"
VIDISPINE_PORT=8080
VIDISPINE_USERNAME="fakeuser"
VIDISPINE_PASSWORD="fakepassword"

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher'
]


MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
