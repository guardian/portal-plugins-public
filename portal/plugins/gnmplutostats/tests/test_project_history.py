import unittest2
import os
import xml.etree.cElementTree as ET


class TestProjectHistory(unittest2.TestCase):
    def test_loads(self):
        """
        ProjectHistory should load a changeset document and convert it into an array of ProjectHistoryChange objects
        :return:
        """
        from portal.plugins.gnmplutostats.project_history import ProjectHistory

        p = ProjectHistory("VX-123",load_now=False)
        with open(os.path.join(os.path.dirname(__file__), "data/test_changeset_data.xml"),"r") as f:
            xmldata = ET.fromstring(f.read())

        result = p._process_xml_doc(xmldata)
        self.assertEqual(len(result),9)

        self.assertEqual(result[0].user,"system")
        self.assertEqual(result[0].fieldname,"title")
        self.assertEqual(result[0].newvalue,"On The Road")

    def test_changes_for_field(self):
        """
        ProjectHistory should filter available changesets by field
        :return:
        """
        from portal.plugins.gnmplutostats.project_history import ProjectHistory, ProjectHistoryChange

        p = ProjectHistory("VX-123",load_now=False)
        p.changes = [
            ProjectHistoryChange("field1","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T00:00:00Z","fred","value1"),
            ProjectHistoryChange("field2","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T01:00:00Z","fred","value2"),
            ProjectHistoryChange("field1","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T02:00:00Z","fred","value3"),
        ]

        result = p.changes_for_field("field2")
        self.assertEqual(len(result),1)
        self.assertEqual(result,[ProjectHistoryChange("field2","66BC6490-8FAA-445E-9D09-EA38708C1FA6","2018-01-01T01:00:00Z","fred","value2")])
        result = p.changes_for_field('field1')
        self.assertEqual(len(result),2)
