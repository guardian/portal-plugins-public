from portal.generic.baseviews import ClassView
from django.http import HttpResponse
from django.shortcuts import render
from forms import LogSearchForm
import logging

def make_vidispine_request(agent,method,urlpath,body,headers,content_type='application/xml'):
    import base64
    from django.conf import settings
    import re
    auth = base64.encodestring('%s:%s' % (settings.VIDISPINE_USERNAME, settings.VIDISPINE_PASSWORD)).replace('\n', '')

    headers['Authorization']="Basic %s" % auth
    headers['Content-Type']=content_type
    #conn.request(method,url,body,headers)
    if not re.match(r'^/',urlpath):
        urlpath = '/' + urlpath

    url = "{0}:{1}{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,urlpath)
    logging.debug("URL is %s" % url)
    (headers,content) = agent.request(url,method=method,body=body,headers=headers)
    return (headers,content)

def getFileInfo(fileid,agent=None):
    import json
    if agent is None:
        import httplib2
        agent = httplib2.Http()

    url = "/API/storage/file/{0}".format(fileid)

    (headers,content) = make_vidispine_request(agent,"GET",url,body="",headers={'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        logging.error(content)
        raise StandardError("Vidispine error: %s" % headers['status'])

    return json.loads(content)

def doJobSearch(url):
    import httplib2
    import json
    from pprint import pprint
    agent = httplib2.Http()
    (headers,content) = make_vidispine_request(agent,"GET",url,body="",headers={'Accept': 'application/json'})

    if int(headers['status']) < 200 or int(headers['status']) > 299:
        logging.error(content)
        raise StandardError("Vidispine error: %s" % headers['status'])

    rtndata = json.loads(content)
    print url
    #pprint(rtndata)

    for row in rtndata['job']:
        if 'data' in row:
            for entry in row['data']:
                row[entry['key']] = entry['value']
                #if len(entry['value']) > 76:
                #    row[entry['key']] = entry['value'][:76] + "..."
                try:
                    if entry['key'] == 'fileId':
                        row['sourceFile'] = getFileInfo(entry['value'],agent)
                except:
                    pass
                try:
                    if entry['key'] == 'destinationFileId':
                        row['destFile'] = getFileInfo(entry['value'],agent)
                except:
                    pass
            del row['data']
    return rtndata

def index(request):
    from pprint import pprint
    from datetime import datetime,timedelta,date,time

    search_results = None
    search_error = None
    page_size=100
    page=1

    if request.method=="POST":
        form = LogSearchForm(request.POST)

        vsurl=""
        try:
          vsurl = form.vidispine_query_url("/API/job")
          search_results = doJobSearch(vsurl)
        except LogSearchForm.FormNotValid as e:
          logging.warning(e)
          print e
        except ValueError as e:
          search_error = "Unable to understand reply from Vidispine: {0}".format(e)
        except StandardError as e:
          search_error = str(e) + " contacting {0}".format(vsurl)

    elif request.method=="GET":
        form = LogSearchForm(initial={
          'type': ['all'],
          'state': ['all'],
          'sort': 'startTime',
          'sortOrder': 'desc',
          'fromDate': datetime.now().date() - timedelta(days=1),
          'fromTime': time(hour=0,minute=0,second=0),
          'toDate': datetime.now().date(),
          'toTime': datetime.now().time(),
        })
    else:
      raise HttpResponse("Invalid method",status=400)

    pprint(search_results)

    results = None
    if search_results is not None and 'job' in search_results:
      results = search_results['job']

    hits = None
    if search_results is not None and 'hits' in search_results:
      hits = search_results['hits']

    return render(request,"logsearch.html", {'search_form': form,'search_results': results,'search_error': search_error, 'search_hits': hits })

