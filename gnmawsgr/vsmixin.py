from xml.etree.cElementTree import Element,SubElement,tostring
import time
from threading import Thread, currentThread


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


class VSMixin(object):
    """
    Class to perform Vidispine search for purgemeister
    """
    _ns = "{http://xml.vidispine.com/schema/vidispine}"
    
    #only return these fields. Saves a LOT of time for metadata-heavy items.
    #overload this in a mixed-in class to get your own list of fields.
    interesting_fields = [
        'created',
        'title',
        'gnm_asset_category',
        'original_filename',
    ]
    
    vidispine_url = ""
    vidispine_port = 0
    
    def __init__(self):
        from django.conf import settings
        self.vidispine_url = settings.VIDISPINE_URL
        self.vidispine_port = settings.VIDISPINE_PORT

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
        
        (headers,content) = agent.request(url,method=method,body=body,headers=headers)

        st = int(headers['status'])
        if st < 200 or st > 299:
            raise HttpError(url,method, body, headers, content)

        return (headers,content)


class VSFuture(Thread, VSMixin):
    """
    Scala-style asynchronous request for Vidispine. Usage:
    myrequst = VSFuture(None,"GET","/API/requestpath","",{})
    myrequst.start()
    .
    .
    .
    (headers, content) = myreqst.waitfor()
    or:
    parsed_object = myreqst.waitfor_json()
    """
    import httplib2
    
    class TimeoutError(StandardError):
        pass
    
    def __init__(self, agent, method, urlpath, body, headers, content_type='application/xml', *args, **kwargs):
        super(VSFuture, self).__init__(*args, **kwargs)
        
        self.agent = agent if agent else self.httplib2.Http()
        self.method = method if method else "GET"
        self.urlpath = urlpath
        self.body = body
        self.headers = headers
        self.content_type = content_type
        
        self.eventual_value = None
        self.error = None
        self._tid = None
    
    def run(self):
        self._tid = currentThread()
        try:
            self.eventual_value = self._make_vidispine_request(self.agent, self.method, self.urlpath, self.body,
                                                               self.headers, self.content_type)
        except Exception as e:
            self.error = e  # defer the error to be raised in waitfor()
    
    def start(self):
        super(VSFuture, self).start()
        return self
    
    def did_complete(self):
        """
        :return:  True if there is either a successful result or an error
        """
        if self.eventual_value is None and self.error is None:
            return False
        else:
            return True
    
    def waitfor(self, timeout=30):
        """
        suspend current thread awaiting the result from the future.  Any exceptions that were raised in the thread
        are re-raised in the main thread by this method.
        If you are expecting a JSON result then use the waitfor_json method with does the same but also parses the returned content
        :param timeout: timeout in seconds.  If this is reached, then VSFuture.TimeoutError is raised.
        :return: tuple of (headers, content) from the HTTP request
        """
        start_time = time.time()
        self.join(timeout=timeout)
        
        while self.eventual_value is None and self.error is None:
            time.sleep(1)
            if time.time() > start_time + timeout:
                raise self.TimeoutError("Request timed out")
        
        if self.error is not None:
            raise self.error
        
        return self.eventual_value
    
    def waitfor_json(self, timeout=30):
        """
        convenience method to wait for the result of the request and then parse it as a JSON object
        :param timeout: timeout in seconds. If this is reached, then VSFuture.TimeoutError is raised.
        :return: json object (list or dictionary)
        """
        import json
        (headers, content) = self.waitfor(timeout=timeout)
        return json.loads(content)


class VSWrappedSearch(object):
    """
    Perform a vidispine search using VSFuture

    search = VSWrappedSearch({'key': 'value'}).execute
    .
    .
    .
    data = search.waitfor_json()
    """
    
    def __init__(self, metadata, pagesize=10):
        if isinstance(metadata, dict):
            self.meta_query = [metadata]
        elif hasattr(metadata, '__iter__'):  # any other iterable, assume it's a list of dict
            self.meta_query = metadata
        else:
            raise TypeError
        
        self.pagesize = pagesize
    
    def make_searchdoc(self):
        """
        builds a search document from the provided metadata.
        metadata is held as a list; each item in the list should be a dictionary.
        each dictionary element is combined with an AND operator (all items in the dictionary field_name=>value) must match;
        each of these operators are combined with a global OR operator (any dictionary can match, but must match fully)
        :return: string of the built XML document
        """
        root_el = Element("ItemSearchDocument", {'xmlns': 'http://xml.vidispine.com/schema/vidispine'})
        container_el = SubElement(root_el, "operator", {'operation': 'OR'})
        
        for query in self.meta_query:
            query_root = SubElement(container_el, "operator", {'operation': 'AND'})
            for k, v in query.items():
                field_el = SubElement(query_root, "field")
                SubElement(field_el, "name").text = k
                if not hasattr(v, '__iter__'):
                    values = [v]
                else:
                    values = v
                
                for val in values:
                    SubElement(field_el, "value").text = val
        return tostring(root_el)
    
    def execute(self, http=None, start_at=1, fieldlist=None):
        if fieldlist is not None:
            querypart = "?content=metadata&field=" + ",".join(fieldlist)
        else:
            querypart = ""
            
        return VSFuture(http, "PUT", "/API/item;first={0};number={1}{2}".format(start_at, self.pagesize, querypart),
                        self.make_searchdoc(),
                        {'Accept': 'application/json'}
                        ).start()