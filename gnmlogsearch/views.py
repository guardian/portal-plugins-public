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
                if len(entry['value']) > 76:
                    row[entry['key']] = entry['value'][:76] + "..."
            del row['data']
    return rtndata

def index(request):
  from pprint import pprint

  search_results = None
  search_error = None
  if request.method=="POST":
      form = LogSearchForm(request.POST)
      vsurl=""
      try:
          vsurl = form.vidispine_query_url("/API/job")
          search_results = doJobSearch(vsurl)
      except LogSearchForm.FormNotValid as e:
          logging.warning(e)
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

