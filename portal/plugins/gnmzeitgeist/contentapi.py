from httplib2 import Http
from django.core.cache import get_cache
import json
import logging

CACHE_TIMEOUT = 24 * 3600 * 7   #cache content api responses for a week

class HttpError(StandardError):
    pass

def lookup_tag(taglist):
    cache = get_cache('default')

    if not isinstance(taglist,list):
        taglist = [taglist]

    rtnlist = []

    h = None

    for capitag in taglist:
        cache_key = "capi:" + capitag
        logging.info(capitag)
        response = cache.get(cache_key)
        if response is not None:
            rtnlist.append(response)
            continue

        if h is None:
            h = Http()

        uri = "http://internal.content.guardianapis.com/{0}?page-size=0".format(capitag)
        (headers, content) = h.request(uri,method="GET",headers={'Accept': 'application/json'})

        if headers.status < 200 or headers.status > 299:
            raise HttpError("{0} returned {1}".format(uri,headers.status))

        data = json.loads(content)

        cache.set(cache_key,data['response']['tag'],CACHE_TIMEOUT)
        rtnlist.append(data['response']['tag'])

    if len(rtnlist) == 1:
        return rtnlist[0]

    return rtnlist