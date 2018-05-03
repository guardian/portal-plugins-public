class HttpError(StandardError):
    """
    Class to represent a generic HTTP error (non-2xx response)
    """
    def __init__(self, url, method, sent_body, headers, content):
        self.url = url
        self.method = method
        self.sent_body = sent_body
        self.headers = headers
        self.content = content

    def __unicode__(self):
        if 'status' in self.headers:
            status = self.headers['status']
        elif 'status_code' in self.headers:
            status = self.headers['status_code']
        else:
            status = 'unknown'
        return u'HTTP error {0} accessing {1}. Content: {2}'.format(status,self.url,self.content)

    def __str__(self):
        return self.__unicode__().encode('ascii')

from django.conf import settings


class VSMixin(object):
    """
    Class to perform Vidispine search for purgemeister
    """
    #only return these fields. Saves a LOT of time for metadata-heavy items.
    interesting_fields = [
        'created',
        'title',
        'gnm_asset_category',
        'original_filename',
    ]
    vidispine_url = settings.VIDISPINE_URL
    vidispine_port = settings.VIDISPINE_PORT

    def _make_vidispine_request(self,agent,method,urlpath,body,headers,content_type='application/xml'):
        """
        Private method to send a request to Vidispine
        :param agent:  initialised httplib2 Http() instance
        :param method: request method - GET, PUT, POST, etc.
        :param urlpath: URL subpath to access, including the /API/ part
        :param body: request body to send (if any)
        :param headers: dictionary of extra headers to send
        :param content_type: MIME type of body content (if sent)
        :return: tuple of headers, content from httplib. Raises HttpError if response was not 2xx.
        """
        import logging
        from django.conf import settings
        import re
        import base64
        auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

        headers['Authorization']="Basic %s" % auth
        headers['Content-Type']=content_type
        #conn.request(method,url,body,headers)
        if not re.match(r'^/',urlpath):
            urlpath = '/' + urlpath

        url = "{0}:{1}{2}".format(self.vidispine_url,self.vidispine_port,urlpath)
        logging.debug("URL is %s" % url)
        (headers,content) = agent.request(url,method=method,body=body,headers=headers)

        st = int(headers['status'])
        if st < 200 or st > 299:
            raise HttpError(url,method, body, headers, content)

        return (headers,content)


class StorageCapacityMixin(object):

    def get_storage_capacity(self,storage_id):
        import requests
        from requests.auth import HTTPBasicAuth
        response = requests.get("{0}:{1}/API/storage/{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,storage_id),
                                auth=HTTPBasicAuth(settings.VIDISPINE_USERNAME,settings.VIDISPINE_PASSWORD),
                                headers={'Accept': 'application/json'})

        if response.status_code==200:
            returned_data = response.json()
            fields = ['id','state','type','capacity','freeCapacity']
            rtn = {}
            for f in fields:
                rtn[f] = returned_data[f]
            return rtn
        else:
            raise HttpError(url="{0}:{1}/API/storage/{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,storage_id),
                            method="GET",
                            sent_body="",
                            headers=response.headers,
                            content=response.text)

