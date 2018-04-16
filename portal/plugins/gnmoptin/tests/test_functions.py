import django.test
import logging
import os
from django.core.management import execute_from_command_line

logging.basicConfig(level=logging.DEBUG)
os.environ["CI"] = "True"  #simulate a CI environment even if we're not in one, this will stop trying to import portal-specific stuff
#which breaks the tests
import portal.plugins.gnmoptin.tests.django_test_settings as django_test_settings

os.environ["DJANGO_SETTINGS_MODULE"] = "portal.plugins.gnmoptin.tests.django_test_settings"
if(os.path.exists(django_test_settings.DATABASES['default']['NAME'])):
    os.unlink(django_test_settings.DATABASES['default']['NAME'])
execute_from_command_line(['manage.py','syncdb',"--noinput"])
execute_from_command_line(['manage.py','migrate',"--noinput"])
execute_from_command_line(['manage.py','loaddata',"users.yaml"])
execute_from_command_line(['manage.py','loaddata',"optins.yaml"])


class TestFunctions(django.test.TestCase):
    fixtures = [
        "users",
        "optins"
    ]

    def test_exists_enabled(self):
        """
        userfeature should return True when a feature is enabled for a given user
        :return:
        """
        from django.contrib.auth.models import User
        from portal.plugins.gnmoptin.functions import userfeature

        testuser = User.objects.get(pk=1)
        result = userfeature(testuser, "swanky stuff")
        self.assertEqual(result, True)

    def test_exists_disabled(self):
        """
        userfeature should return False when a feature is not enabled for a given user
        :return:
        """
        from django.contrib.auth.models import User
        from portal.plugins.gnmoptin.functions import userfeature

        testuser = User.objects.get(pk=2)
        result = userfeature(testuser, "swanky stuff")
        self.assertEqual(result, False)

    def test_exists_notexists(self):
        """
        userfeature should return False when no feature is present for the given user
        :return:
        """
        from django.contrib.auth.models import User
        from portal.plugins.gnmoptin.functions import userfeature

        testuser = User.objects.get(pk=1)
        result = userfeature(testuser, "fsdsdfsdfsdfs")
        self.assertEqual(result, False)
