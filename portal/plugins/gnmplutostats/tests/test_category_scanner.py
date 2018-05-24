import unittest2
from mock import MagicMock, patch

class TestFindCategories(unittest2.TestCase):
    from helpers import MockResponse
    def test_find_categories(self):
        """
        find_categories should return a list of categories
        :return:
        """
        testdoc = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ItemListDocument xmlns="http://xml.vidispine.com/schema/vidispine">
    <hits>1691985</hits>
    <facet>
        <field>gnm_asset_category</field>
        <count fieldValue="Rushes">1165113</count>
        <count fieldValue="Completed Project">169266</count>
        <count fieldValue="HoldingImage">41071</count>
    </facet>
</ItemListDocument>"""

        with patch('requests.put', return_value=self.MockResponse(200, testdoc)):
            from portal.plugins.gnmplutostats.categoryscanner import find_categories
            result = find_categories()
            self.assertEqual(result, ['Rushes','Completed Project', 'HoldingImage'])