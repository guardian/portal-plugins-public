from __future__ import absolute_import
import os
import django.test
from rest_framework.test import APIClient
from django.core.urlresolvers import reverse
from django.core.management import execute_from_command_line
import portal.plugins.kinesisresponder.tests.django_test_settings as django_test_settings
import logging

logging.basicConfig(level=logging.DEBUG)

os.environ["DJANGO_SETTINGS_MODULE"] = "portal.plugins.kinesisresponder.tests.django_test_settings"

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py','loaddata',"users.yaml"])
execute_from_command_line(['manage.py','loaddata',"kinesis_tracker.yaml"])

class TestViews(django.test.TestCase):
    fixtures = [
        'kinesis_tracker',
        'users'
    ]

    def test_message_list_view(self):
        """
        message_list_view should return a list of messages to an admin user
        :return:
        """
        from django.contrib.auth.models import User

        client = APIClient()

        client.force_authenticate(user=User.objects.get(username='admin'))
        response = client.get(reverse("message_list_view", kwargs={'stream_name': "teststream"}))
        self.assertTrue(isinstance(response.data,list))
        self.assertEqual(1, len(response.data))
        self.assertDictContainsSubset({
            "shard_id": "shardId-000000000000",
            "millis_behind_latest": 1240000
        }, response.data[0])