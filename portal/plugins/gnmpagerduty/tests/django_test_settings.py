import os
BASE_DIR = "/tmp"
SECRET_KEY = 'v7j%&)-4$(p&tn1izbm0&#owgxu@w#%!*xn&f^^)+o98jxprbe'
INSTALLED_APPS = ['portal.plugins.gnmpagerduty','south','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions']
ROOT_URLCONF = 'portal.plugins.gnmpagerduty.urls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'djangotestdb.sqlite3'),
    }
}

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

VIDISPINE_URL="http://localhost"
VIDISPINE_PORT=8080
VIDISPINE_USERNAME="fakeuser"
VIDISPINE_PASSWORD="fakepassword"

PAGERDUTY_KEY="blahblahblahblah"
