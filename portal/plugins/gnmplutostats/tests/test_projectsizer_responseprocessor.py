import unittest2
from mock import MagicMock, patch
import os


class TestResponseProcessor(unittest2.TestCase):
    def test_loads(self):
        """
        ResponseProcessor should load in a vidispine response and give back total items and the number contained in the response
        :return:
        """
        from portal.plugins.gnmplutostats.projectsizer import ResponseProcessor

        with open(os.path.join(os.path.dirname(__file__), "data/sample_response_1.xml"),"r") as f:
            p = ResponseProcessor(f.read())
            self.assertEqual(p.total_hits, 1855)
            self.assertEqual(p.entries, 3)

    def test_sums(self):
        """
        ResponseProcessor should sum the contents of a page
        :return:
        """
        from portal.plugins.gnmplutostats.projectsizer import ResponseProcessor, ProcessResult
        from pprint import pprint

        with open(os.path.join(os.path.dirname(__file__), "data/sample_response_1.xml"),"r") as f:
            p = ResponseProcessor(f.read())
            result = ProcessResult()

            p.page_size(result,"original")
            self.assertDictEqual(result.storage_sum,{'KP-8': 1.2787874639034271})
