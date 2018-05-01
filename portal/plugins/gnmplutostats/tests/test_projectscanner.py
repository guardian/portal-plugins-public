import unittest2
from mock import MagicMock, patch
import os
from django.core.management import execute_from_command_line
from django.conf import settings
from requests.auth import HTTPBasicAuth

class TestProjectInfo(unittest2.TestCase):
    def test_build(self):
        """
        ProjectInfo should initialise itself from an XML fragment
        :return:
        """
        import xml.etree.cElementTree as ET
        from portal.plugins.gnmplutostats.projectscanner import ProjectInfo
        bodycontent = """<collection xmlns="http://xml.vidispine.com/schema/vidispine">
        <id>KP-30946</id>
        <name>Monbiot Meets (series circa 2008)</name>
        <metadata>
            <revision>KP-26079827,KP-26079760,KP-26079789,KP-26079770,KP-26079799</revision>
            <timespan start="-INF" end="+INF">
                <field uuid="37d5489e-f0b9-467d-97a0-745aa61095c4" user="david_allison" timestamp="2018-04-30T15:27:40.159+01:00" change="KP-26079760">
                    <name>gnm_project_status</name>
                    <value uuid="a4b95647-4410-4334-8ee8-6797564ddd1d" user="david_allison" timestamp="2018-04-30T15:27:40.159+01:00" change="KP-26079760">New</value>
                </field>
            </timespan>
        </metadata>
    </collection>"""
        xmlcontent = ET.fromstring(bodycontent)

        info = ProjectInfo(xmlcontent)

        self.assertEqual(info.name,"KP-30946")
        self.assertEqual(info.title,"Monbiot Meets (series circa 2008)")
        self.assertEqual(info.status, "New")


class TestProjectScanner(unittest2.TestCase):
    from helpers import MockResponse

    def setUp(self):
        if settings.DATABASES['default']['NAME']=="":
            raise ValueError("tests misconfigured, need a local database path")
        if os.path.exists(settings.DATABASES['default']['NAME']):
            os.unlink(settings.DATABASES['default']['NAME'])

        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])

    def tearDown(self):
        pass

    def test_scan_next_page(self):
        """
        scan_next_page should request the next page of results from vidispine
        :return:
        """
        with open(os.path.join(os.path.dirname(__file__), "data/sample_project_list.xml"),"r") as f:
            project_size_content = f.read()

        with patch('requests.put', return_value=self.MockResponse(200,project_size_content)) as mock_put:
            from portal.plugins.gnmplutostats.projectscanner import ProjectScanner

            s = ProjectScanner()
            results = map(lambda x: x, s.scan_next_page(1,3))
            self.assertEqual(len(results),3)

            self.assertEqual(results[0].title,"Monbiot Meets (series circa 2008)")
            self.assertEqual(results[0].name,"KP-30946")
            self.assertEqual(results[0].status,"New")

            self.assertEqual(results[1].title,"Cholera Outbreak Zimbabwe")
            self.assertEqual(results[1].name,"KP-30945")
            self.assertEqual(results[1].status,"New")

            self.assertEqual(results[2].title,"The True Cost of Pineapples")
            self.assertEqual(results[2].name,"KP-30944")
            self.assertEqual(results[2].status,"New")

            mock_put.assert_called_once_with('http://localhost:8080/API/collection;first=1;number=3?content=metadata&field=gnm_project_status',
                                             auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
                                             data='<ItemSearchDocument xmlns="http://xml.vidispine.com/schema/vidispine">\n            <field>\n                <name>gnm_type</name>\n                <value>project</value>\n            </field>\n        </ItemSearchDocument>', headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'})

    def test_scan_next_page_error(self):
        """
        scan_next_page should raise an HTTPException if it gets a non-200 response
        :return:
        """
        with patch('requests.put', return_value=self.MockResponse(503,"")) as mock_put:
            from portal.plugins.gnmplutostats.projectscanner import ProjectScanner

            with self.assertRaises(ProjectScanner.HttpError) as raise_excep:
                s = ProjectScanner()
                results = map(lambda x: x, s.scan_next_page(1,3))
            self.assertEqual(raise_excep.exception.status_code,503)