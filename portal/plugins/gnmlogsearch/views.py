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
    import json
    
    search_results = None
    search_error = None
    page_size=100
    page=1

    if request.method=="POST":
        form = LogSearchForm(request.POST)

        pagepost = request.POST['page'][:]

        pagenow = int(pagepost)

        if request.POST.get("nextthisisauniquename"):
            page = pagenow + 1

        if request.POST.get("previousthisisauniquename"):
            page = pagenow - 1

        vsurl=""
        try:
          vsurl = form.vidispine_query_url("/API/job", page)
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
          'toTime': datetime.now().strftime("%H:%M:%S"),
          'columns': ['jobId', 'status', 'type', 'started', 'priority', 'itemid', 'systemJobModule', 'systemJobInfo', 'destinationStorageId', 'bestEffortFilename', 'fileId', 'replicatedFileIds', 'fileDeleted', 'fileStateOnFailure', 'filePathMap', 'replicatedFileInfo', 'checkReplicatedFiles'],
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

    columnsettings = dict()

    if request.method=="POST":
        postdata = dict(request.POST.iterlists())

        if u'jobId' in postdata['columns']:
            columnsettings['jobId'] = 'true'

        if u'status' in postdata['columns']:
            columnsettings['status'] = 'true'

        if u'type' in postdata['columns']:
            columnsettings['type'] = 'true'

        if u'started' in postdata['columns']:
            columnsettings['started'] = 'true'

        if u'priority' in postdata['columns']:
            columnsettings['priority'] = 'true'

        if u'itemid' in postdata['columns']:
            columnsettings['itemid'] = 'true'

        if u'systemJobModule' in postdata['columns']:
            columnsettings['systemJobModule'] = 'true'

        if u'systemJobInfo' in postdata['columns']:
            columnsettings['systemJobInfo'] = 'true'

        if u'destinationStorageId' in postdata['columns']:
            columnsettings['destinationStorageId'] = 'true'

        if u'bestEffortFilename' in postdata['columns']:
            columnsettings['bestEffortFilename'] = 'true'

        if u'fileId' in postdata['columns']:
            columnsettings['fileId'] = 'true'

        if u'replicatedFileIds' in postdata['columns']:
            columnsettings['replicatedFileIds'] = 'true'

        if u'fileDeleted' in postdata['columns']:
            columnsettings['fileDeleted'] = 'true'

        if u'fileStateOnFailure' in postdata['columns']:
            columnsettings['fileStateOnFailure'] = 'true'

        if u'filePathMap' in postdata['columns']:
            columnsettings['filePathMap'] = 'true'

        if u'replicatedFileInfo' in postdata['columns']:
            columnsettings['replicatedFileInfo'] = 'true'

        if u'checkReplicatedFiles' in postdata['columns']:
            columnsettings['checkReplicatedFiles'] = 'true'

        #page = int(request.POST['page'][:])

    prev_page = 0
    next_page = None

    if hits > page_size and (hits - (page * page_size)) > 1:
        next_page = page + 1

    if hits > page_size and page > 1:
        prev_page = page - 1

    last_result = 1

    if hits is not None:
        if (hits + 100) < (page * 100 + 100):
            last_result = hits
        else:
            last_result = page * 100

    first_result = page * 100 - 100 + 1

    if 'accept' in request.GET and request.GET['accept'] == 'application/json':
        return HttpResponse(content=json.dumps({'status': 'ok', 'hits': hits, 'results': search_results}),status=200)
    return render(request,"logsearch.html", {'search_form': form,'search_results': results,'search_error': search_error, 'search_hits': hits, 'columnsettings': columnsettings, 'next_page': next_page, 'prev_page': prev_page, 'page': page, 'first_result': first_result, 'last_result': last_result})

