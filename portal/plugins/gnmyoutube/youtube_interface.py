#Requires the google client api library

from pprint import pprint
import httplib2
from apiclient.discovery import build

class YoutubeInterface:
    YOUTUBE_READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
    YOUTUBE_ADMIN_SCOPE = 'https://www.googleapis.com/auth/youtube'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    def __init__(self):
        self._credentials = None
        self.youtube_service = None
        pass

    def authorize_pki(self,client_id,pki,scope=YOUTUBE_ADMIN_SCOPE,as_user=None):
        from oauth2client.client import SignedJwtAssertionCredentials
        self._credentials = SignedJwtAssertionCredentials(client_id,pki,scope,sub=as_user)

        h = self._credentials.authorize(httplib2.Http())
        self.youtube_service = build(self.YOUTUBE_API_SERVICE_NAME,self.YOUTUBE_API_VERSION,http=h)

    def list_categories(self,region_code='gb'):
        result = self.youtube_service.videoCategories().list(part="id,snippet",regionCode=region_code).execute()

        #pprint(result)
        return result