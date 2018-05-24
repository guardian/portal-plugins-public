import unittest2
from mock import MagicMock, patch
import os
from requests.auth import HTTPBasicAuth
from django.conf import settings
import xml.etree.cElementTree as ET

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

        with open(os.path.join(os.path.dirname(__file__), "data/sample_response_1.xml"), "r") as f:
            p = ResponseProcessor(f.read())
            result = ProcessResult()

            p.page_size(result,"original")
            self.assertDictEqual(result.storage_sum,{'KP-8': 1.2787874639034271})

    def test_get_right_component(self):
        from portal.plugins.gnmplutostats.projectsizer import ResponseProcessor
        samplexml = """<?xml version="1.0"?>
<ns0:shape xmlns:ns0="http://xml.vidispine.com/schema/vidispine">
  <ns0:id>KP-2742667</ns0:id>
  <ns0:essenceVersion>0</ns0:essenceVersion>
  <ns0:tag>original</ns0:tag>
  <ns0:mimeType>application/xml</ns0:mimeType>
  <ns0:binaryComponent>
    <ns0:file>
      <ns0:id>KP-34814589</ns0:id>
      <ns0:path>Multimedia_News/Sex_Robots/tom_silverstone_Sex_Robots/PornExpo/A019C878_170118RY_CANON.XML</ns0:path>
      <ns0:uri>omms://90d35ae3-52c6-11e4-83c3-eadf79e8d4b9:_VSENC__DcKSYaC+uU66Z0rPeUjzPsqwu4l9wV2wwx0Y9KRRy4iMfxOHFGSsvA==@10.236.51.145/38b7c064-a862-0fe2-44cd-7191ca6201c3/90688ac0-52c6-11e4-ad57-f3b682b37806/Multimedia_News/Sex_Robots/tom_silverstone_Sex_Robots/PornExpo/A019C878_170118RY_CANON.XML</ns0:uri>
      <ns0:state>CLOSED</ns0:state>
      <ns0:size>467</ns0:size>
      <ns0:hash>a1b05d6f09f0a9e64258f7d6c26280a2e7e62ad6</ns0:hash>
      <ns0:timestamp>2017-05-08T00:21:33.114+01:00</ns0:timestamp>
      <ns0:refreshFlag>1</ns0:refreshFlag>
      <ns0:storage>KP-3</ns0:storage>
      <ns0:metadata>
        <ns0:field>
          <ns0:key>MXFS_PARENTOID</ns0:key>
          <ns0:value/>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATION_TIME</ns0:key>
          <ns0:value>1494185842114</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATIONDAY</ns0:key>
          <ns0:value>7</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CATEGORY</ns0:key>
          <ns0:value>4</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>created</ns0:key>
          <ns0:value>1484779255000</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ACCESS_TIME</ns0:key>
          <ns0:value>1494185842148</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHDAY</ns0:key>
          <ns0:value>7</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_INTRASH</ns0:key>
          <ns0:value>false</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>mtime</ns0:key>
          <ns0:value>1484779255000</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHYEAR</ns0:key>
          <ns0:value>2017</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>uuid</ns0:key>
          <ns0:value>ccc26cb9-3355-11e7-ad57-f3b682b37806-18</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>path</ns0:key>
          <ns0:value>.</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHIVE_TIME</ns0:key>
          <ns0:value>1494185842114</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_MODIFICATION_TIME</ns0:key>
          <ns0:value>1494185842148</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATIONYEAR</ns0:key>
          <ns0:value>2017</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHMONTH</ns0:key>
          <ns0:value>5</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_FILENAME_UPPER</ns0:key>
          <ns0:value>MULTIMEDIA_NEWS/SEX_ROBOTS/TOM_SILVERSTONE_SEX_ROBOTS/PORNEXPO/A019C878_170118RY_CANON.XML</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATIONMONTH</ns0:key>
          <ns0:value>5</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_FILENAME</ns0:key>
          <ns0:value>Multimedia_News/Sex_Robots/tom_silverstone_Sex_Robots/PornExpo/A019C878_170118RY_CANON.XML</ns0:value>
        </ns0:field>
      </ns0:metadata>
    </ns0:file>
    <ns0:file>
      <ns0:id>KP-34814592</ns0:id>
      <ns0:path>Multimedia_News/Sex_Robots/tom_silverstone_Sex_Robots/PornExpo/A019C878_170118RY_CANON.XML</ns0:path>
      <ns0:uri>omms://32bd5db9-52ca-11e4-9515-877ef3241ca7:_VSENC__gM%2FYdAoCKA2QhYNVGGEujw6t2p+j0Ulj4Ub62Rhft7mRqTzTG8W26T2bqqQpiAjO@10.235.51.145/5ce37552-358f-998b-115b-9569b8f21a01/32aae714-52ca-11e4-9515-877ef3241ca7/Multimedia_News/Sex_Robots/tom_silverstone_Sex_Robots/PornExpo/A019C878_170118RY_CANON.XML</ns0:uri>
      <ns0:state>CLOSED</ns0:state>
      <ns0:size>467</ns0:size>
      <ns0:hash>a1b05d6f09f0a9e64258f7d6c26280a2e7e62ad6</ns0:hash>
      <ns0:timestamp>2017-05-08T21:28:38.840+01:00</ns0:timestamp>
      <ns0:refreshFlag>1</ns0:refreshFlag>
      <ns0:storage>KP-2</ns0:storage>
      <ns0:metadata>
        <ns0:field>
          <ns0:key>MXFS_PARENTOID</ns0:key>
          <ns0:value/>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATION_TIME</ns0:key>
          <ns0:value>1494185842689</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATIONDAY</ns0:key>
          <ns0:value>7</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CATEGORY</ns0:key>
          <ns0:value>4</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>created</ns0:key>
          <ns0:value>1484779255000</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ACCESS_TIME</ns0:key>
          <ns0:value>1494252189584</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHDAY</ns0:key>
          <ns0:value>7</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_INTRASH</ns0:key>
          <ns0:value>false</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>mtime</ns0:key>
          <ns0:value>1484779255000</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHYEAR</ns0:key>
          <ns0:value>2017</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>uuid</ns0:key>
          <ns0:value>56fc554e-335a-11e7-b151-a08e23ea6ced-5</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>path</ns0:key>
          <ns0:value>.</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHIVE_TIME</ns0:key>
          <ns0:value>1494185842689</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_MODIFICATION_TIME</ns0:key>
          <ns0:value>1494185842740</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATIONYEAR</ns0:key>
          <ns0:value>2017</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_ARCHMONTH</ns0:key>
          <ns0:value>5</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_FILENAME_UPPER</ns0:key>
          <ns0:value>MULTIMEDIA_NEWS/SEX_ROBOTS/TOM_SILVERSTONE_SEX_ROBOTS/PORNEXPO/A019C878_170118RY_CANON.XML</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_CREATIONMONTH</ns0:key>
          <ns0:value>5</ns0:value>
        </ns0:field>
        <ns0:field>
          <ns0:key>MXFS_FILENAME</ns0:key>
          <ns0:value>Multimedia_News/Sex_Robots/tom_silverstone_Sex_Robots/PornExpo/A019C878_170118RY_CANON.XML</ns0:value>
        </ns0:field>
      </ns0:metadata>
    </ns0:file>
    <ns0:id>KP-6572228</ns0:id>
    <ns0:length>467</ns0:length>
  </ns0:binaryComponent>
</ns0:shape>"""
        content = ET.fromstring(samplexml)

        result = ResponseProcessor.get_right_component(content)
        self.assertEqual(result,"{0}binaryComponent".format(ResponseProcessor.xmlns))

        samplexml2 = """<shape xmlns="http://xml.vidispine.com/schema/vidispine">
            <id>KP-3353686</id>
            <essenceVersion>0</essenceVersion>
            <tag>original</tag>
            <mimeType>audio/mp4</mimeType>
            <containerComponent>
                <file>
                    <id>KP-41978064</id>
                    <path>Multimedia_Documentaries/The_Gene_gap/noah_payne_frank_The_Gene_gap/temp music and video/02 I'm in the Pink.m4a</path>
                    <uri>file:///srv/Multimedia2/Media%20Production/Assets/Multimedia_Documentaries/The_Gene_gap/noah_payne_frank_The_Gene_gap/temp%20music%20and%20video/02%20I'm%20in%20the%20Pink.m4a</uri>
                    <state>CLOSED</state>
                    <size>4640687</size>
                    <hash>da895a3491b0f8ccd09fa485ef2e2c50f7197ec3</hash>
                    <timestamp>2018-04-21T14:55:46.215+01:00</timestamp>
                    <refreshFlag>1</refreshFlag>
                    <storage>KP-8</storage>
                    <metadata/>
                </file>
                <id>KP-8129263</id>
            </containerComponent>
        </shape>"""
        content2 = ET.fromstring(samplexml2)

        result2 = ResponseProcessor.get_right_component(content2)
        self.assertEqual(result2,"{0}containerComponent".format(ResponseProcessor.xmlns))

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