from __future__ import absolute_import
from rest_framework.test import APITestCase, APIClient
from mock import MagicMock, patch
from django.core.management import execute_from_command_line
from django.core.urlresolvers import reverse, reverse_lazy
import os
import django.test
import json

import portal.plugins.gnmatomresponder.tests.django_test_settings as django_test_settings

os.environ["DJANGO_SETTINGS_MODULE"] = "portal.plugins.gnm_projects.tests.django_test_settings"
if(os.path.exists(django_test_settings.DATABASES['default']['NAME'])):
    os.unlink(django_test_settings.DATABASES['default']['NAME'])

execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'loaddata', 'fixtures/ImportJobs.yaml'])


# Store original __import__
orig_import = __import__

### Patch up imports for  stuff that is not in this project
models_mock = MagicMock()
constants_mock = MagicMock()
constants_mock.GNM_MASTERS_MEDIAATOM_ATOMID = "fake_media_atom_id"


def import_mock(name, *args, **kwargs):
    if name == 'portal.plugins.gnm_masters.models' or name=='gnm_masters.models':
        return models_mock
    elif name == 'portal.plugins.gnm_vidispine_utils.constants':
        return constants_mock
    return orig_import(name, *args, **kwargs)


class TestAPIViews(APITestCase):
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

    #unfortunately can't easily test job_list_view, because it uses the custom django tag templateextends and I can't work
    #out how to mock it at the moment.


class TestResyncToAtomApiView(APITestCase):
    class MockResponse(object):
        def __init__(self, status_code, json_dict):
            self.status_code = status_code
            self.json_dict = json_dict

        def json(self):
            return self.json_dict

        def content(self):
            return str(self.json_dict)

    def test_resync_normal(self):
        """
        a request should trigger a resync
        :return:
        """
        client = APIClient()

        mock_master = MagicMock()
        mock_master.get = MagicMock(return_value="09239f72-e0a5-4299-ba5e-ec18c27117b4")
        with patch('__builtin__.__import__', side_effect=import_mock):
            with patch('requests.put', return_value=self.MockResponse(200,{"some": "data","here":"now"})) as mock_put:
                #with patch("portal.plugins.gnm_masters.models.VSMaster", return_value=mock_master):
                models_mock.VSMaster = MagicMock(return_value=mock_master)
                response = client.get(reverse_lazy("resync_to_atom", kwargs={"item_id":"VX-123"}))
                self.assertEqual(response.status_code,200)
                self.assertDictEqual(json.loads(response.content),{"some": "data","here":"now"})
                mock_put.assert_called_once_with("https://launchdetector/update/09239f72-e0a5-4299-ba5e-ec18c27117b4")

