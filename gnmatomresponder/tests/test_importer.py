import datetime
import logging
import os.path

import unittest2
from boto import kinesis
from django.core.management import execute_manager
from mock import patch

logging.basicConfig(level=logging.DEBUG)

import django_test_settings as django_test_settings

os.environ["DJANGO_SETTINGS_MODULE"] = "django_test_settings"
if(os.path.exists(django_test_settings.DATABASES['default']['NAME'])):
    os.unlink(django_test_settings.DATABASES['default']['NAME'])

execute_manager(django_test_settings,['manage.py','syncdb'])
execute_manager(django_test_settings,['manage.py','migrate'])


class TestImporter(unittest2.TestCase):
    def test_make_pluto_holding_image(self):
        from gnmatomresponder.master_importer import MasterImportResponder
        import json

        conn = kinesis.connect_to_region('eu-west-1')
        r = MasterImportResponder(conn,"test_stream","noshard")

        jsondata = r.make_pluto_holding_image("https://path/to/some/image.jpg")
        decoded = json.loads(jsondata)

        self.assertEqual(decoded,{'url_16x9': "https://path/to/some/image.jpg",
                                  'id_16x9': "",
                                  'filename_16x9': "image.jpg"})

    def test_process(self):
        from gnmatomresponder.master_importer import MasterImportResponder

        testdatapath = os.path.realpath(os.path.dirname(__file__)) + "/data/atom_response.json"
        conn = kinesis.connect_to_region('eu-west-1')
        r = MasterImportResponder(conn,"test_stream","noshard")

        with open(testdatapath,"r") as f:
            content = f.read()

        with patch('gnmvidispine.vs_item.VSItem.createPlaceholder') as mockcreate:
            testlog = "{0} Imported from media atom tool".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            r.process(content,datetime.datetime.now())

            mockcreate.assert_called_once_with(
                {'gnm_asset_category': 'Master',
                 'gnm_asset_status': 'Ready for Editing',
                 'gnm_asset_user_keywords': [u'Champions League',
                                             u'Barcelona',
                                             u'Real Madrid',
                                             u'Atletico Madrid',
                                             u'Bayern Munich',
                                             u'Dortmund',
                                             u'Monaco',
                                             u'Leicester City',
                                             u'Juventus',
                                             u'Football',
                                             u'Sport'],
                 'gnm_master_mediaatom_atomid': u'18de147b-059f-4bc1-8d9a-c7150718518a',
                 'gnm_master_mediaatom_status': 'Published',
                 'gnm_master_mediaatom_uploadlog': testlog,
                 'gnm_master_mediaatom_uploadstatus': 'Upload Succeeded',
                 'gnm_master_publication_time': datetime.datetime(2017, 3, 17, 7, 39, 58),
                 'gnm_master_website_byline': u'Test User',
                 'gnm_master_website_headline': u'Champions League quarter-final draw: Leicester to face Atl\xe9tico Madrid \u2013 video',
                 'gnm_master_website_holdingimage': '{"id_16x9": "", "url_16x9": "https://media.guim.co.uk/95ac3a59042cd8779c655c10bbdb31a49e3579e4/0_23_4763_2680/4763.jpg", "filename_16x9": "4763.jpg"}',
                 'gnm_master_website_item_published': 'live',
                 'gnm_master_website_standfirst': u"Leicester City will take on Atl\xe9tico Madrid in the last eight of the Champions League after the draw for the quarter-final stage of this season's competition took place on Friday. Dortmund will play Monaco, Bayern Munich meet Real Madrid and Barcelona take on Juventus",
                 'gnm_master_website_upload_log': testlog,
                 'gnm_master_website_uploadstatus': 'Upload Succeeded',
                 'gnm_master_youtube_allowcomments': '',
                 'gnm_master_youtube_category': u'17',
                 'gnm_master_youtube_channelid': u'cvdsKJvdshkvdss',
                 'gnm_master_youtube_description': u"Leicester City will take on Atl\xe9tico Madrid in the last eight of the Champions League after the draw for the quarter-final stage of this season's competition took place on Friday. Dortmund will play Monaco, Bayern Munich meet Real Madrid and Barcelona take on Juventus",
                 'gnm_master_youtube_keywords': [u'Champions League',
                                                 u'Barcelona',
                                                 u'Real Madrid',
                                                 u'Atletico Madrid',
                                                 u'Bayern Munich',
                                                 u'Dortmund',
                                                 u'Monaco',
                                                 u'Leicester City',
                                                 u'Juventus',
                                                 u'Football',
                                                 u'Sport'],
                 'gnm_master_youtube_publication_date_and_time': datetime.datetime(2017, 3, 17, 7, 39, 58),
                 'gnm_master_youtube_title': u'Champions League quarter-final draw: Leicester to face Atl\xe9tico Madrid \u2013 video',
                 'title': u'Champions League quarter-final draw: Leicester to face Atl\xe9tico Madrid \u2013 video'},
                group='Asset'
            )