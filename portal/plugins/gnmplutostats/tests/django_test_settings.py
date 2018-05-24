import os
BASE_DIR = "/tmp"
SECRET_KEY = 'vfkjnvdj,nxvzzvdxdvn,mvxd'
INSTALLED_APPS = ['portal.plugins.gnmplutostats', 'django.contrib.auth', 'django.contrib.contenttypes',
                  'django.contrib.sessions','south']
ROOT_URLCONF = 'portal.plugins.gnmplutostats.urls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_CHARSET': 'UTF-8',
        'NAME': ":memory:",
        'TEST_NAME': ":memory:"
    }
}

VIDISPINE_URL="http://localhost"
VIDISPINE_PORT=8080
VIDISPINE_USERNAME="fakeuser"
VIDISPINE_PASSWORD="fakepassword"

