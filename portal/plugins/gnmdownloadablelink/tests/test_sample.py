from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

# This is an example of tests for portal. To run these tests, start by installing all the test requirements:
#
# /opt/cantemo/python/bin/pip install -r /opt/cantemo/portal/test-requirements.pip
#
# Then run:
#
# /opt/cantemo/portal/manage.py test portal.plugins.gnmdownloadablelink


class TestExamples(TestCase):

    def setUp(self):
        super(TestExamples, self).setUp()
        # Do any setup here

    def tearDown(self):
        super(TestExamples, self).tearDown()
        # Do any teardown here

    def test_example_view_requires_auth(self):
        response = self.client.get(reverse("gnmdownloadablelink:index"))
        self.assertEqual(response.status_code, 302)

    def test_example_view_get(self):
        self.client.login(username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD)
        response = self.client.get(reverse("gnmdownloadablelink:index"))
        self.assertEqual(response.status_code, 200)
