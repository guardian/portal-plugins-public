import unittest2
from mock import MagicMock, patch
import os
from requests.auth import HTTPBasicAuth
from django.conf import settings


class TestResponseProcessor(unittest2.TestCase):
    def test_loads(self):
        """
        ResponseProcessor should load in a vidispine response and give back total items and the number contained in the response
        :return:
        """
        from portal.plugins.gnmplutostats.projectsizer import ResponseProcessor

        with open(os.path.join(os.path.dirname(__file__), "data/sample_response_1.xml"), "r") as f:
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

        with open(os.path.join(os.path.dirname(__file__), "data/sample_response_1.xml"), "r") as f:
            p = ResponseProcessor(f.read())
            result = ProcessResult()

            p.page_size(result,"original")
            self.assertDictEqual(result.storage_sum,{'KP-8': 1.2787874639034271})


class TestProjectSizer(unittest2.TestCase):
    from helpers import MockResponse

    def test_process_next_page(self):
        """
        process_next_page should download the next page of results
        :return:
        """
        with open(os.path.join(os.path.dirname(__file__), "data/sample_response_1.xml"),"r") as f:
            project_size_content = f.read()

            with patch('requests.put', return_value=self.MockResponse(200,project_size_content)) as mock_put:
                from portal.plugins.gnmplutostats.projectsizer import process_next_page, ProcessResult

                result = ProcessResult()

                process_next_page("VX-1234", result, 1, 20)

                mock_put.assert_called_once_with('http://localhost:8080/API/item;first=1;number=20?content=shape',
                                                 auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
                                                 data='<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">\n        <field>\n            <name>__collection</name>\n            <value>VX-1234</value>\n        </field>\n    </ItemSearchDocument>',
                                                 headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

                self.assertDictEqual(result.storage_sum,{'KP-8': 1.2787874639034271})