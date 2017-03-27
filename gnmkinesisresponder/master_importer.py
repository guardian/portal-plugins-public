from kinesis_responder import KinesisResponder
import json
from pprint import pprint
from urlparse import urlparse
import os.path


class MasterImportResponder(KinesisResponder):
    ITEM_MD_GROUP = 'Asset'

    def make_pluto_holding_image(self, imageurl):
        #        {
        #   "url_16x9":"/APInoauth/thumbnail/KP-5/KP-1788214;version=0/0?hash=9e53947f0317bf35e8043c172ba17f4a",
        #   "id_16x9":"KP-1788214",
        #   "filename_16x9":"image.png",
        #   "url_4x3":"/APInoauth/thumbnail/KP-5/KP-1788215;version=0/0?hash=e37a58143c2e93a417408a5ea8794130",
        #   "id_4x3":"KP-1788215",
        #   "filename_4x3":"image.png"
        #}

        splitdown = urlparse(imageurl)

        return json.dumps({
            "url_16x9": imageurl,
            "id_16x9": "",
            "filename_16x9": os.path.basename(splitdown.path)
        })

    def process(self,record, approx_arrival):
        from atom_message import AtomMessage
        from gnmvidispine.vs_item import VSItem
        from gnmvidispine.vs_collection import VSCollection
        from django.conf import settings
        from datetime import datetime
        content = AtomMessage(record)

        # project_collection = VSCollection(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        # project_collection.populate(content['project_id'])
        #
        # commission_collection = VSCollection(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        # commission_collection.populate(project_collection.get('__collection'))

        uploadlog = "{0} Imported from media atom tool".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        metadata = {
            'title': content.title,
            'gnm_asset_category': 'Master',
            'gnm_asset_status': 'Ready for Editing',
            'gnm_asset_user_keywords': content.tags,

            'gnm_master_mediaatom_atomid': content.id,
            'gnm_master_mediaatom_status': 'Published', #can we get a proper value for this?
            'gnm_master_mediaatom_uploadlog': uploadlog,
            'gnm_master_mediaatom_uploadstatus': 'Upload Succeeded',

            'gnm_master_website_headline': content.title,
            'gnm_master_website_standfirst': content.description,
            # 'gnm_master_website_tags': #we can't set this at the moment because media atom maker only has free-text tags.

            'gnm_master_website_byline': content.contentChangeDetails['created']['user']['firstName'] + " " + content.contentChangeDetails['created']['user']['lastName'],
            'gnm_master_website_holdingimage': self.make_pluto_holding_image(content.biggest_poster_image().file),
            'gnm_master_website_uploadstatus': 'Upload Succeeded',
            'gnm_master_website_item_published': "live",
            'gnm_master_website_upload_log': uploadlog,

            'gnm_master_youtube_title': content.title,
            'gnm_master_youtube_description': content.description,
            'gnm_master_youtube_keywords': content.tags,
            'gnm_master_youtube_category': content.youtubeCategoryId,
            'gnm_master_youtube_channelid': content.channelId,
            'gnm_master_youtube_allowcomments': 'allow_comments' if content.commentsEnabled else "",
            #'gnm_master_youtube_containsadultcontent' - not defined in atom model - should be??
        }

        if 'published' in content.contentChangeDetails:
            metadata['gnm_master_publication_time'] = datetime.fromtimestamp(content.contentChangeDetails['published']['date']/1000)
            metadata['gnm_master_youtube_publication_date_and_time'] = datetime.fromtimestamp(content.contentChangeDetails['published']['date']/1000)

        pprint(metadata)
        item = VSItem(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
        item.createPlaceholder(metadata,group=self.ITEM_MD_GROUP)

