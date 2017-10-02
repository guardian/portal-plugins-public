import os
BASE_DIR = "/tmp"
SECRET_KEY = 'v=YkST56UIq05jJ5Gn40UstWYd0+8G/Lu03EjOnSYds1/bafiSYUhiWwzaRjjtQ'
INSTALLED_APPS = ['portal.plugins.gnmlibrarytool',
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'south']

ROOT_URLCONF = 'portal.plugins.gnmlibrarytool.tests.django_test_rooturls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'djangotestdb.sqlite3'),
    }
}

VIDISPINE_URL="http://localhost"
VIDISPINE_PORT=8080
VIDISPINE_USERNAME="fakeuser"
VIDISPINE_PASSWORD="fakepassword"

TEMPLATE_DIRS = (
    'gnmlibrarytool/templates/gnmlibrarytool'
)

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
