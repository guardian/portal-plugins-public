import os.path

import unittest2


class TestAtomMessage(unittest2.TestCase):
    TEST_DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "data/atom_response.json"))

    def test_parse_and_get(self):
        from portal.plugins.gnmatomresponder.atom_message import AtomMessage
        with open(self.TEST_DATA_FILE) as f:
            a = AtomMessage(f.read())

        self.assertEqual(a.description,u"Leicester City will take on Atl\xe9tico Madrid in the last eight of the Champions League after the draw for the quarter-final stage of this season's competition took place on Friday. Dortmund will play Monaco, Bayern Munich meet Real Madrid and Barcelona take on Juventus")
        self.assertEqual(a.category, u"News")
        self.assertEqual(a.duration, 66)
        with self.assertRaises(ValueError):
            v = a.somethinginvalid

    def test_poster_images(self):
        from portal.plugins.gnmatomresponder.atom_message import AtomMessage
        with open(self.TEST_DATA_FILE) as f:
            a = AtomMessage(f.read())

        image_list = map(lambda x: x, a.posterImages)
        self.assertEqual(len(image_list), 5)

        print image_list[0].__repr__()
        self.assertEqual(image_list[0].mimeType,"image/jpeg")
        self.assertEqual(image_list[0].size,186874)

    def test_biggest_poster_image(self):
        from portal.plugins.gnmatomresponder.atom_message import AtomMessage
        with open(self.TEST_DATA_FILE) as f:
            a = AtomMessage(f.read())

        imageinfo = a.biggest_poster_image()
        self.assertEqual(imageinfo.file,"https://media.guim.co.uk/95ac3a59042cd8779c655c10bbdb31a49e3579e4/0_23_4763_2680/4763.jpg")
        self.assertEqual(imageinfo.size,980993)

    def test_assets(self):
        from portal.plugins.gnmatomresponder.atom_message import AtomMessage
        with open(self.TEST_DATA_FILE) as f:
            a = AtomMessage(f.read())

        assetinfo = map(lambda x: x, a.assets)

        self.assertEqual(len(assetinfo),1)
        self.assertEqual(assetinfo[0].version,1)
        self.assertEqual(assetinfo[0].external_id,"hXOwkMb5V1w")
        self.assertEqual(assetinfo[0].assetType,"Video")
        self.assertEqual(assetinfo[0].platform,"Youtube")

    def test_latest_asset(self):
        from portal.plugins.gnmatomresponder.atom_message import AtomMessage
        with open(self.TEST_DATA_FILE) as f:
            a = AtomMessage(f.read())

        assetinfo = a.latest_asset

        self.assertEqual(assetinfo.version,1)
        self.assertEqual(assetinfo.external_id,"hXOwkMb5V1w")
        self.assertEqual(assetinfo.assetType,"Video")
        self.assertEqual(assetinfo.platform,"Youtube")

    def test_json_error(self):
        from portal.plugins.gnmatomresponder.atom_message import AtomMessage
        import re
        with open(self.TEST_DATA_FILE) as f:
            originalcontent = f.read()
        with self.assertRaises(ValueError):
            a = AtomMessage(originalcontent[1:])    #corrupt the json by removing the opening brace
        with self.assertRaises(ValueError):
            a = AtomMessage(re.sub(r'"',"'",originalcontent)) #corrupt the json by switching ' for "
        with self.assertRaises(ValueError):
            a = AtomMessage(originalcontent[:30])   #corrupt the json by truncating