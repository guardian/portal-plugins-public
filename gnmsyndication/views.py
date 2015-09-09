from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree as ET
import datetime
import dateutil
import logging
from django.conf import settings
import re
from models import platform
logging.basicConfig(level=logging.DEBUG)

#FIXME: need to put these into a model and make configurable
date_fields = [
    'gnm_master_publication_time',
    'gnm_master_mainstreamsyndication_publication_time',
    'gnm_master_dailymotion_publication_time',
    #'gnm_master_youtube_publication_time',
]

def index(request):
  from forms import TimePeriodSelector,DownloadReportForm
  from datetime import datetime
  #return HttpResponse(content="Hello world!",content_type="text/plain",status=200)
  known_platforms = platform.objects.all()

  current_date = datetime.now()
  m = current_date.month
  y = current_date.year

  try:
      if 'selected_month' in request.GET:
          m = int(request.GET['selected_month'])
      if 'selected_year' in request.GET:
          y = int(request.GET['selected_year'])
  except ValueError as e:
      logging.error(str(e))

  selectorform = TimePeriodSelector(initial={'selected_month': m,'selected_year': y})
  start = current_date
  start.replace(day=1)
  downloadform = DownloadReportForm(initial={'start_time': start, 'end_time': current_date})

  return render(request,"syndicationstats.html", {'platforms': known_platforms,'time_period_selector': selectorform,
  'downloadform': downloadform})

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

    try:
        if 'selected_month' in request.GET and 'selected_year' in request.GET:
            start_time = datetime.datetime(int(request.GET['selected_year']),int(request.GET['selected_month'])+1,1) - number * intervalTime
        elif 'selected_month' in request.GET:
            temp = datetime.datetime.now()
            start_time = datetime.datetime(temp.year,int(request.GET['selected_month'])+1,1) - number * intervalTime
    except ValueError as e:
        logging.error(str(e))

    if start_time is None:
        start_time = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) - number * intervalTime



    requeststring = "<ItemSearchDocument xmlns=\"http://xml.vidispine.com/schema/vidispine\">"

    for fieldname in date_fields:
        requeststring += make_facet_xml(fieldname,start_time=start_time)
    requeststring += "</ItemSearchDocument>"

    logging.debug(requeststring)

    agent = httplib2.Http()

    (headers,content) = make_vidispine_request(agent,"PUT","/API/item;number=0",requeststring,{'Accept': 'application/json'})
    if int(headers['status']) < 200 or int(headers['status']) > 299:
        raise StandardError("Vidispine error: %s" % headers['status'])

    data=json.loads(content)

    if not 'facet' in data:
        raise StandardError("Vidispine did not return faceted data when requested")

    rtn = {'totals': {},'data': []}
    reformatted_data = {}

    for facet in data['facet']:
        fieldname = facet['field']
        #parts = re.match(r'^gnm_master_(.*)_publication_time$',facet['field'])
        #if parts:
        #    fieldname = parts.group(1)

        for value in facet['range']:
            timestamp = mktimestamp(value['start'])
            if not timestamp in reformatted_data:
                reformatted_data[timestamp] = []
            reformatted_data[timestamp].append({
                facet['field']: int(value['value'])
            })
            if fieldname in rtn['totals']:
                rtn['totals'][fieldname] += int(value['value'])
            else:
                rtn['totals'][fieldname] = int(value['value'])

    for k,v in reformatted_data.items():
        entry = {"timestamp": k}
        for datum in v:
            entry.update(datum)
        rtn['data'].append(entry)
    #rtn = sorted(rtn,key=lambda x: x['timestamp'])
    return HttpResponse(json.dumps(rtn),content_type="application/json",status=200)

def asset_list_by_day(request,date):
    from xml.etree.ElementTree import Element, SubElement, Comment, tostring
    import httplib2
    import json

    interesting_fields = [
        'title',
        'durationSeconds',
        'gnm_master_website_headline',
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
        'gnm_master_pacdata_status',
        'gnm_master_website_keyword_ids',
        #===========
        'gnm_master_generic_whollyowned',
        'gnm_master_generic_ukonly',
        'gnm_master_generic_containsadultcontent',
        'gnm_master_generic_preventmobileupload',
        'gnm_master_generic_source',
        'gnm_master_mainstreamsyndication_keywords',
        'gnm_master_youtube_keywords'
    ]
    if isinstance(date,datetime.datetime):
        dt = date
    else:
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
    limit = 50
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
            'url': 'http://pluto.gnm.int/master/{0}'.format(itemdata['id']),
            'itemId': itemdata['id'],
        }
        for f in interesting_fields:
            ref[f] = ""
        for field in itemdata['metadata']['timespan'][0]['field']:
            if 'value' in field:
                ref[field['name']] = []
                for v in field['value']:
                    ref[field['name']].append(v['value'].encode('UTF-8'))
                if len(ref[field['name']]) == 1:
                    ref[field['name']] = ref[field['name']][0]
                try:
                    pass
                    #ref[field['name']] = datetime.datetime.strptime(ref[field['name']],"%Y-%m-%dT%H:%M:%SZ")
                except:
                    pass
        assets.append(ref)
    return assets

#date is string, dd/mm/yyyy
def assets_by_day(request,date):
    assets = asset_list_by_day(request,date)
    #return HttpResponse(json.dumps(assets),content_type='application/json',status=200)
    return render(request,"syndication_filedetails.html",{"items": assets})

def seconds_to_duration(nsec):
    m, s = divmod(nsec, 60)
    h, m = divmod(m, 60)
    #print "%d:%02d:%02d" % (h, m, s)
    return u"%02d:%02d:%02d" % (h,m,s)

def csv_report(request):
    from StringIO import StringIO
    from datetime import datetime, timedelta
    from pprint import pprint
    import csv

    if not 'start_date' in request.GET or not 'end_date' in request.GET:
        pprint(request.GET)
        raise ValueError("You need to pass start_date and end_date as a get value")
    # try:
    #     month = int(request['selected_month'])
    # except ValueError as e:
    #     raise ValueError("selected_month must be an integer")

    interval = timedelta(days=1)
    try:
        start_date = datetime.strptime(request.GET['start_date'],"%d/%m/%Y")
    except ValueError as e:
        raise ValueError("start_date should be in the format dd/mm/YYYY")
    try:
        end_date = datetime.strptime(request.GET['end_date'],"%d/%m/%Y")
    except ValueError as e:
        raise ValueError("end_date should be in the format dd/mm/YYYY")

    fout = StringIO()
    csvout = csv.writer(fout)
    have_header = False
    # interesting_fields = [
    #     'title',
    #     'gnm_master_headline',
    #     'gnm_master_website_uploadstatus',
    #     'gnm_master_mainstreamsyndication_uploadstatus',
    #     'gnm_master_dailymotion_uploadstatus',
    #     'gnm_master_youtube_uploadstatus',
    #     'gnm_master_publication_time',
    #     'gnm_master_mainstreamsyndication_publication_time',
    #     'gnm_master_dailymotion_publication_time',
    #     'gnm_master_generic_intendeduploadplatforms',
    #     'gnm_commission_title',
    #     'gnm_project_headline',
    #     'gnm_master_pacdata_status',
    #     'gnm_master_website_keyword_ids'
    # ]
    current_date = start_date
    while current_date < end_date:
        try:
            asset_list = asset_list_by_day(request,current_date)
        except StandardError as e:
            return HttpResponse(str(e),status=500,content_type='text/plain')

        if not have_header:
            csvout.writerow(['Headline','URL','Duration','Keywords (Mainstream)', 'Source', 'Commission',
                             'Project', 'Wholly owned?', 'UK Only', 'Explicit content', 'No mobile rights',
                             'Published to website','Published to Mainstream',
                             'Published to Daily Motion','Keyword IDs'])
            have_header = True

        if asset_list:
            for row in asset_list:
                csvout.writerow([row['gnm_master_website_headline'],
                                row['url'],
                                seconds_to_duration(row['durationSeconds']),
                                row['gnm_master_mainstreamsyndication_keywords'],
                                row['gnm_master_generic_source'],
                                row['gnm_commission_title'],
                                row['gnm_project_headline'],
                                row['gnm_master_generic_whollyowned'],
                                row['gnm_master_generic_ukonly'],
                                row['gnm_master_generic_containsadultcontent'],
                                row['gnm_master_generic_preventmobileupload'],
                                row['gnm_master_publication_time'],
                                row['gnm_master_mainstreamsyndication_publication_time'],
                                row['gnm_master_dailymotion_publication_time'],
                                row['gnm_master_website_keyword_ids']])
        current_date += interval

    rtn = fout.getvalue()
    #csvout.close()
    fout.close()

    return HttpResponse(rtn,status=200,content_type='text/csv')
