from portal.generic.baseviews import ClassView
from django.http import HttpResponse

import logging

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

    xmlroot = Element("ItemSearchDocument",{'xmlns': 'http://xml.vidispine.com/schema/vidispine'})

    fieldsearch = SubElement(xmlroot,"field")
    fieldsearchname = SubElement(fieldsearch,"name")
    fieldsearchname.text = "gnm_type"
    fieldsearchvalue = SubElement(fieldsearch,"value")
    fieldsearchvalue.text = "Master"

    facetroot = SubElement(xmlroot,"facet", {'count': "true"})
    facetfield = SubElement(facetroot,"field")
    facetfield.text = "gnm_master_website_keyword_ids"

    xmlstring = tostring(xmlroot,encoding="UTF-8")

    agent = httplib2.Http()
    (headers, content) = make_vidispine_request(agent,"PUT","/API/item;number=0",xmlstring,{'Accept': 'application/json'})

    return HttpResponse(content,content_type='application/json',status=200)
