import json
import dateutil.parser
import httplib2
import re
from pprint import pprint, pformat
__author__ = "Andy Gallagher <andy.gallagher@theguardian.com>"


WEBSERVICE_BASE = "http://internal.content.guardianapis.com"
WEBSERVICE_ARGS = "?format=json&show-fields=all&show-tags=all&show-elements=all&order-by=newest&api-key=gnm-multimedia-updater"


class HttpError(StandardError):
    pass


isdate = re.compile(r'Date')
isnum = re.compile(r'^\d+$')

def update_data_types(record):
    for k,v in record.items():
        if isinstance(v,dict):
            record[k] = update_data_types(v)
        elif isinstance(v,basestring):
            if isdate.search(k):
                try:
                    record[k] = dateutil.parser.parse(v)
                except:
                    pass
            elif isnum.match(v):
                try:
                    record[k] = int(v)
                except:
                    pass
            elif v=='false':
                record[k] = False
            elif v=='true':
                record[k] = True
    return record


def lookup_by_octid(octid):
    if not re.match(r'^\d+$',octid):
        raise ValueError("octopus id must be a number")

    weburl = WEBSERVICE_BASE + "/internal-code/octopus/" + octid + WEBSERVICE_ARGS

    h = httplib2.Http()

    (headers, content) = h.request(weburl,method="GET")
    #pprint(headers)

    if int(headers['status'])<200 or int(headers['status'])>299:
        raise HttpError(headers['status'])

    data = json.loads(content)
    #pprint(data)
    return update_data_types(data['response']['content'])

#internal.content.guardianapis.com/search?q={internalComposerCode}
#gives results[] section with each occurrence of it on the site

if __name__ == "__main__":
    import sys
    record = lookup_by_octid(sys.argv[1])
    pprint(record)