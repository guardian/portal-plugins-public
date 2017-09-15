from __future__ import absolute_import
import django.test
from mock import MagicMock, patch
from django.core.management import execute_from_command_line
from django.core.urlresolvers import reverse, reverse_lazy
import os

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/ImportJobs.yaml'])


class TestTasks(django.test.TestCase):
    fixtures = [
        'ImportJobs'
    ]

    def test_cleanup_old_importjobs(self):
        """
        cleanup_old_importjobs should purge out jobs older than 60 days
        :return:
        """
        from portal.plugins.gnmatomresponder.models import ImportJob
        from portal.plugins.gnmatomresponder.tasks import cleanup_old_importjobs
        #FIXME: still need to patch datetime.now() to always return the same value
        self.assertEqual(ImportJob.objects.all().count(), 5)
        cleanup_old_importjobs()
        self.assertEqual(ImportJob.objects.all().count(), 4)