from __future__ import absolute_import
from rest_framework.test import APITestCase, APIClient
from mock import MagicMock, patch
from django.core.management import execute_from_command_line
from django.core.urlresolvers import reverse, reverse_lazy
import os
import django.test


class TestViews(APITestCase):
    fixtures = [
        "links","users"
    ]

    def test_get_link_noauth(self):
        client = APIClient()

        result = client.get(reverse_lazy("downloadable_link_item", kwargs={'pk': 1}))

        self.assertEqual(result.status_code, 403)

    def test_get_link_valid(self):
        from django.contrib.auth.models import User
        import datetime

        client = APIClient()
        client.force_authenticate(user=User.objects.get(pk=1))
        result = client.get(reverse_lazy("downloadable_link_item", kwargs={'pk': 1}))

        self.assertEqual(result.status_code, 200)
        self.assertDictEqual(result.data,
                             {"public_url": "",
                              "status": "Requested",
                              "created": datetime.datetime(2018, 1, 5, 17, 23, 54, 141470),
                              "created_by": 1,
                              "expiry": datetime.datetime(2018, 1, 5, 17, 23, 54, 143562),
                              "item_id": "VX-11",
                              "shapetag": "original",
                              "transcode_job": ""
                              })

    def test_get_link_invalid(self):
        from django.contrib.auth.models import User

        client = APIClient()
        client.force_authenticate(user=User.objects.get(pk=1))
        result = client.get(reverse_lazy("downloadable_link_item", kwargs={'pk': 20392}))

        self.assertEqual(result.status_code, 404)

    def test_get_links_for_item_valid(self):
        from django.contrib.auth.models import User
        import datetime

        client = APIClient()
        client.force_authenticate(user=User.objects.get(pk=1))
        result = client.get(reverse_lazy("downloadable_links_for_item")+"?itemid=VX-11")

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data),4)
        self.assertEqual(result.data,[
            {'public_url': u'', 'status': u'Requested', 'created': datetime.datetime(2018, 1, 5, 17, 23, 54, 141470), 'created_by': 1, 'expiry': datetime.datetime(2018, 1, 5, 17, 23, 54, 143562), 'item_id': u'VX-11', 'shapetag': u'lowres', 'transcode_job': u''},
            {'public_url': u'', 'status': u'Requested', 'created': datetime.datetime(2018, 1, 5, 17, 23, 54, 141470), 'created_by': 1, 'expiry': datetime.datetime(2018, 1, 5, 17, 23, 54, 143562), 'item_id': u'VX-11', 'shapetag': u'mezzanine', 'transcode_job': u''},
            {'public_url': u'', 'status': u'Requested', 'created': datetime.datetime(2018, 1, 5, 17, 23, 54, 141470), 'created_by': 1, 'expiry': datetime.datetime(2018, 1, 5, 17, 23, 54, 143562), 'item_id': u'VX-11', 'shapetag': u'original', 'transcode_job': u''},
            {'public_url': u'', 'status': u'Requested', 'created': datetime.datetime(2018, 1, 5, 17, 23, 54, 141470), 'created_by': 1, 'expiry': datetime.datetime(2018, 1, 5, 17, 23, 54, 143562), 'item_id': u'VX-11', 'shapetag': u'webm', 'transcode_job': u''}
        ])

        newresult = client.get(reverse_lazy("downloadable_links_for_item")+"?itemid=VX-12")
        self.assertEqual(newresult.status_code, 200)
        self.assertEqual(len(newresult.data),1)
        self.assertEqual(newresult.data, [
            {'public_url': u'', 'status': u'Requested', 'created': datetime.datetime(2018, 1, 5, 17, 23, 54, 141470), 'created_by': 1, 'expiry': datetime.datetime(2018, 1, 5, 17, 23, 54, 143562), 'item_id': u'VX-12', 'shapetag': u'mezzanine', 'transcode_job': u''}
        ])

    def test_get_links_for_item_invalid(self):
        from django.contrib.auth.models import User
        import datetime

        client = APIClient()
        client.force_authenticate(user=User.objects.get(pk=1))
        result = client.get(reverse_lazy("downloadable_links_for_item")+"?itemid=NN-321")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data,[])

    def test_create_link_for(self):
        from django.contrib.auth.models import User
        from celery.result import AsyncResult

        client = APIClient()
        client.force_authenticate(user=User.objects.get(pk=1))

        newdata = {
            'status': 'Requested',
            'created': '2017-01-01T14:32:02',
            'expiry': '2017-01-03T00:00:00',
        }

        mock_celery_result = MagicMock(target=AsyncResult)
        mock_celery_result.id = "B833C61E-A6D6-45B4-A8D1-94927C0898BF"
        with patch("portal.plugins.gnmdownloadablelink.tasks.create_link_for") as mock_create_link_task:
            mock_create_link_task.delay = MagicMock(return_value=mock_celery_result)
            result = client.post(reverse_lazy("downloadable_link_create", kwargs={'item_id': "VX-31", 'shape_tag': "mezzanine"}), newdata, format="json")
            self.assertEqual(result.status_code, 200)

            mock_create_link_task.delay.assert_called_once_with("VX-31","mezzanine")

    def test_create_link_for_invalid(self):
        from django.contrib.auth.models import User
        from celery.result import AsyncResult

        client = APIClient()
        client.force_authenticate(user=User.objects.get(pk=1))

        newdata = {
            'status': 'Requested',
            'created': '2017-01-01T14:32:02',
        }

        mock_celery_result = MagicMock(target=AsyncResult)
        mock_celery_result.id = "B833C61E-A6D6-45B4-A8D1-94927C0898BF"
        with patch("portal.plugins.gnmdownloadablelink.tasks.create_link_for") as mock_create_link_task:
            mock_create_link_task.delay = MagicMock(return_value=mock_celery_result)
            result = client.post(reverse_lazy("downloadable_link_create", kwargs={'item_id': "VX-31", 'shape_tag': "mezzanine"}), newdata, format="json")
            self.assertEqual(result.status_code, 400)

            mock_create_link_task.delay.assert_not_called()
