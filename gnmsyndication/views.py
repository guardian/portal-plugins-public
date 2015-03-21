from portal.generic.baseviews import ClassView
from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree as ET
import datetime
import dateutil
import logging
from django.conf import settings
import re

logging.basicConfig(level=logging.DEBUG)

#FIXME: need to put these into a model and make configurable
date_fields = [
    'gnm_master_publication_time',
    'gnm_master_mainstreamsyndication_publication_time',
    'gnm_master_dailymotion_publication_time',
    #'gnm_master_youtube_publication_time',
]

def index(request):
  #return HttpResponse(content="Hello world!",content_type="text/plain",status=200)
  return render(request,"syndicationstats.html")

def make_facet_xml(fieldname,start_time=None,number=30,intervalTime=datetime.timedelta(days=1)):
    if start_time is None:
        startTime = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) - number * intervalTime
    elif isinstance(start_time,datetime.datetime):
        startTime = start_time
    else:
        startTime = dateutil.parser.parse(start_time)

    logging.debug("Starting at {0} with {1} buckets".format(str(startTime),number))
    logging.debug("Interval time is {0}".format(str(intervalTime)))
    timeformat = "%Y-%m-%dT%H:%M:%SZ"

    #rtn = ""
    rtn = "<facet><field>{0}</field>".format(fieldname)
    for n in range(1,number):
        rangeStart = startTime + (n * intervalTime)
        rangeEnd = startTime + ((n+1) * intervalTime)
        rtn+= '  <range start="{0}" end="{1}"/>'.format(rangeStart.strftime(timeformat),rangeEnd.strftime(timeformat))
    rtn+= "</facet>"

    return rtn

def make_vidispine_request(agent,method,urlpath,body,headers,content_type='application/xml'):
    import base64
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

def mktimestamp(timestring):
    import time
    dt = datetime.datetime.strptime(timestring,"%Y-%m-%dT%H:%M:%SZ")
    return time.mktime(dt.timetuple())

def platforms_by_day(request):
    import httplib2
    import json

    units="days"
    interval=1
    number=30
    start_time = None

    if 'units' in request.GET:
        units=request.GET['units']
    if 'interval' in request.GET:
        interval=int(request.GET['interval'])
    if 'number' in request.GET:
        number=int(request.GET['number'])
    if 'start_time' in request.GET:
        start_time = request.GET['start_time']

    if units == "weeks":
        intervalTime=datetime.timedelta(weeks=interval)
    elif units == "days":
        intervalTime=datetime.timedelta(days=interval)
    elif units == "hours":
        intervalTime=datetime.timedelta(hours=interval)
    elif units == "minutes":
        intervalTime=datetime.timedelta(minutes=interval)
    elif units == "seconds":
        intervalTime=datetime.timedelta(seconds=interval)
    else:
        raise StandardError("Units must be either seconds, minutes, hours, days or weeks")

    if start_time is None:
        start_time = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) - number * intervalTime



    requeststring = "<ItemSearchDocument xmlns=\"http://xml.vidispine.com/schema/vidispine\">"

    for fieldname in date_fields:
        requeststring += make_facet_xml(fieldname)
    requeststring += "</ItemSearchDocument>"

    logging.debug(requeststring)

    agent = httplib2.Http()

    (headers,content) = make_vidispine_request(agent,"PUT","/API/item;number=0",requeststring,{'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        raise StandardError("Vidispine error: %s" % headers['status'])

    data=json.loads(content)

    if not 'facet' in data:
        raise StandardError("Vidispine did not return faceted data when requested")

    rtn = []
    reformatted_data = {}

    for facet in data['facet']:
        for value in facet['range']:
            timestamp = mktimestamp(value['start'])
            if not timestamp in reformatted_data:
                reformatted_data[timestamp] = []
            reformatted_data[timestamp].append({
                facet['field']: int(value['value'])
            })

    for k,v in reformatted_data.items():
        entry = {"timestamp": k}
        for datum in v:
            entry.update(datum)
        rtn.append(entry)
    #rtn = sorted(rtn,key=lambda x: x['timestamp'])
    return HttpResponse(json.dumps(rtn),content_type="application/json",status=200)

def assets_by_day(request,date):
    from xml.etree.ElementTree import Element, SubElement, Comment, tostring
    import httplib2
    import json

    interesting_fields = [
        'title',
        'gnm_master_headline',
        'gnm_master_website_uploadstatus',
        'gnm_master_mainstreamsyndication_uploadstatus',
        'gnm_master_dailymotion_uploadstatus',
        'gnm_master_youtube_uploadstatus',
        'gnm_master_publication_time',
        'gnm_master_mainstreamsyndication_publication_time',
        'gnm_master_dailymotion_publication_time',
        'gnm_master_generic_intendeduploadplatforms',
        'gnm_commission_title',
        'gnm_project_headline',
    ]
    dt = datetime.datetime.strptime(date,"%d/%m/%Y")

    start_time = dt.replace(hour=0,minute=0,second=0,microsecond=0)
    end_time = dt.replace(hour=23,minute=59,second=59,microsecond=999)

    requestroot = Element("ItemSearchDocument", {"xmlns": "http://xml.vidispine.com/schema/vidispine"})

    for f in date_fields:
        sortterm = SubElement(requestroot,"sort")
        sortfield = SubElement(sortterm,"field")
        sortfield.text=f
        sortorder = SubElement(sortterm,"order")
        sortorder.text="descending"

    #oper = SubElement(requestroot,"Operator", {"operation": "OR"})
    #for f in date_fields:
    requestfield = SubElement(requestroot,"field")
    fieldname = SubElement(requestfield,"name")
    fieldname.text = "gnm_master_publication_time"
    fieldrange = SubElement(requestfield,"range")
    fieldstart = SubElement(fieldrange,"value")
    fieldstart.text = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    fieldend = SubElement(fieldrange,"value")
    fieldend.text = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    requeststring = tostring(requestroot)
    logging.debug(requeststring)

    agent = httplib2.Http()

    fields = ",".join(interesting_fields)
    limit = 20
    if 'limit' in request.GET:
        limit=int(request.GET['limit'])

    (headers,content) = make_vidispine_request(agent,"PUT","/API/item?content=metadata&field={0}&n=".format(fields,limit),requeststring,{'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        logging.error(content)
        raise StandardError("Vidispine error: %s" % headers['status'])

    data=json.loads(content)

    assets = []
    for itemdata in data['item']:
        ref = {
            'url': '/master/{0}'.format(itemdata['id']),
        }
        for field in itemdata['metadata']['timespan'][0]['field']:
            if 'value' in field:
                ref[field['name']] = []
                for v in field['value']:
                    ref[field['name']].append(v['value'])
                if len(ref[field['name']]) == 1:
                    ref[field['name']] = ref[field['name']][0]
                try:
                    pass
                    #ref[field['name']] = datetime.datetime.strptime(ref[field['name']],"%Y-%m-%dT%H:%M:%SZ")
                except:
                    pass
        assets.append(ref)

    #return HttpResponse(json.dumps(assets),content_type='application/json',status=200)
    return render(request,"syndication_filedetails.html",{"items": assets})
