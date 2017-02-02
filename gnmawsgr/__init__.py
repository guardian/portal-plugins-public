import os
if not "CI" in os.environ:
    import plugin
    
archive_test_value = 'Archived'
restoring_test_value = 'Requested Restore'
archiving_test_value = 'Requested Archive'


def make_vidispine_request(agent,method,urlpath,body,headers,content_type='application/xml'):
    import base64
    from django.conf import settings
    import re
    auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

    headers['Authorization']="Basic %s" % auth
    headers['Content-Type']=content_type

    if not re.match(r'^/',urlpath):
        urlpath = '/' + urlpath

    url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)
    (headers,content) = agent.request(url,method=method,body=body,headers=headers)
    return (headers,content)

