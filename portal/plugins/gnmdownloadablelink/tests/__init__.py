from django.core.management import execute_from_command_line
import django_test_settings
import os

if os.path.exists(django_test_settings.DATABASES['default']['NAME']):
    os.unlink(django_test_settings.DATABASES['default']['NAME'])

if not 'MANUALTEST' in os.environ:
    execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])