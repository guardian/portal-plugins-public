from __future__ import absolute_import
from rest_framework.test import APITestCase, APIClient
from mock import MagicMock, patch
from django.core.management import execute_from_command_line
from django.core.urlresolvers import reverse, reverse_lazy
import os

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])


class TestViews(APITestCase):
    fixtures = [
        'ImportJobs'
    ]

    @staticmethod
    def _get_test_data(filename):
        mypath = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(mypath, "data", filename)) as f:
            return f.read()

    def test_notification_normal(self):
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        from portal.plugins.gnmatomresponder.models import ImportJob
        client = APIClient()

        data = self._get_test_data("sample_notification.xml")
        mock_notification = MagicMock(target=JobNotification)

        with patch('portal.plugins.gnmatomresponder.notification.process_notification') as mock_process:
            with patch('portal.plugins.gnmatomresponder.job_notification.JobNotification', return_value=mock_notification) as mock_notification_constructor:
                response = client.post(reverse_lazy("import_notification"),data=data,content_type='application/xml')

                self.assertEqual(response.status_code, 200)
                mock_process.assert_called_once_with(mock_notification)
                mock_notification_constructor.assert_called_once_with(data)


    def test_notification_invalidxml(self):
        """
        If the provided XML body does not parse, should return a 400 error
        :return:
        """
        from portal.plugins.gnmatomresponder.job_notification import JobNotification
        client = APIClient()

        data = self._get_test_data("sample_notification.xml")
        truncated_data = data[0:250]

        with patch('portal.plugins.gnmatomresponder.notification.process_notification') as mock_process:
            response = client.post(reverse_lazy("import_notification"),data=truncated_data,content_type='application/xml')

            self.assertEqual(response.status_code, 400)
            self.assertDictEqual(response.data, {'status': 'Bad XML'})
            mock_process.assert_not_called()

    def test_notification_xmlerror(self):
        """
        If another Xml exception is raised, should send a 500 error
        :return:
        """
        from lxml.etree import XMLSyntaxError, LxmlError
        client = APIClient()

        data = self._get_test_data("sample_notification.xml")

        with patch('portal.plugins.gnmatomresponder.notification.process_notification') as mock_process:
            with patch('portal.plugins.gnmatomresponder.job_notification.JobNotification', side_effect=LxmlError("Nobody expects the Spanish Inqusition!")) as mock_notification_constructor:
                response = client.post(reverse_lazy("import_notification"),data=data,content_type='application/xml')

                self.assertEqual(response.status_code, 500)
                mock_notification_constructor.assert_called_once_with(data)
                mock_process.assert_not_called()
