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
        return u'HTTP error {0} accessing {1}. Content: {2}'.format(self.headers['status'],self.url,self.content)

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
    _ns = "{http://xml.vidispine.com/schema/vidispine}"
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