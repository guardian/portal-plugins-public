from portal.generic.baseviews import ClassView
from django.http import HttpResponse
import logging
import contentapi
import re

def index(request):
    from django.shortcuts import render
    #return HttpResponse(content="Hello world!",content_type="text/plain",status=200)
    return render(request,"gnmzeitgeist.html")


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


def data(request):
    import httplib2
    from xml.etree.ElementTree import Element, SubElement, Comment, tostring
    import json
    from django.shortcuts import render
    #from pprint import pprint

    normalise = 42
    if 'n' in request.GET:
        normalise = int(request.GET['n'])

    maxtags = 30
    if 'max' in request.GET:
        maxtags = int(request.GET['max'])

    interesting_field = "gnm_master_website_keyword_ids"
    if 'field' in request.GET:
        interesting_field = request.GET['field']

    xmlroot = Element("ItemSearchDocument",{'xmlns': 'http://xml.vidispine.com/schema/vidispine'})

    fieldsearch = SubElement(xmlroot,"field")
    fieldsearchname = SubElement(fieldsearch,"name")
    fieldsearchname.text = "gnm_type"
    fieldsearchvalue = SubElement(fieldsearch,"value")
    fieldsearchvalue.text = "Master"

    facetroot = SubElement(xmlroot,"facet", {'count': "true"})
    facetfield = SubElement(facetroot,"field")
    facetfield.text = interesting_field

    xmlstring = tostring(xmlroot,encoding="UTF-8")

    agent = httplib2.Http()
    (headers, content) = make_vidispine_request(agent,"PUT","/API/item;number=0",xmlstring,{'Accept': 'application/json'})

    vsdata = json.loads(content)
    if 'notfound' in vsdata:
        logging.error(vsdata)
        raise StandardError("Vidispine error - field not found")

    totalhits = -1
    rtn = {}

    root = ""

    #http://content.guardianapis.com/uk/uk?page-size=0&api-key=test - look up tag data

    #pprint(vsdata)
    for f in vsdata['facet']:
        rtn[f['field']] = {}
        if root == "":
            root = f['field']
        n = 0
        #pprint(f)
        for v in f['count']:
            if n>=maxtags:
                break
            n+=1
            if v['fieldValue'] == 'type/video':
                continue
            if v['fieldValue'].startswith('tone/'):
                continue

            if totalhits < 0:
                totalhits = v['value']

            rtndata =  {"name": v['fieldValue'],
                        "jsid": re.sub(r'/','_',v['fieldValue'])
            }
            try:
                capidata = contentapi.lookup_tag(v['fieldValue'])
                rtndata['name'] = capidata['webTitle']
                rtndata["type"] =  capidata['type']
                rtndata["section"] = capidata['sectionName']
                rtndata["url"] = capidata['webUrl']
            except StandardError as e:
                logging.warning(str(e))

            print "totalhits are %s, current value is %s so factor is %s" % (float(totalhits),float(v['value']),float(v['value'])/float(totalhits))
            rtndata["score"] = (float(v['value'])/float(totalhits)) * float(normalise)
            rtn[f['field']][v['fieldValue']] = rtndata


    return render(request,"tagsource.html",{'tagdata': rtn[root]})
    #return HttpResponse(json.dumps(rtn),content_type='application/json',status=200)
