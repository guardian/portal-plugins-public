from portal.generic.baseviews import ClassView
from django.http import HttpResponse
import logging
import contentapi
import re
from pprint import pprint
from forms import DataSourceForm,AddSourceForm
from models import datasource

def index(request):
    from django.shortcuts import render
    #return HttpResponse(content="Hello world!",content_type="text/plain",status=200)
    add_source_form = AddSourceForm()
    if 'source' in request.GET:
        data_source_form = DataSourceForm(initial={'source': request.GET['source']})
    else:
        data_source_form = DataSourceForm()
    return render(request,"gnmzeitgeist.html", {'source_form': data_source_form,'add_source_form': add_source_form})


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

    if 'source' in request.GET:
        source = datasource.objects.get(name=request.GET['source'])
    else:
        source = datasource.objects.all()[0]

    #interesting_field = "gnm_master_website_keyword_ids"
    #if 'field' in request.GET:
    #    interesting_field = request.GET['field']


    xmlroot = Element("ItemSearchDocument",{'xmlns': 'http://xml.vidispine.com/schema/vidispine'})

    fieldsearch = SubElement(xmlroot,"field")
    fieldsearchname = SubElement(fieldsearch,"name")
    fieldsearchname.text = "gnm_type"
    fieldsearchvalue = SubElement(fieldsearch,"value")
    fieldsearchvalue.text = "Master"

    facetroot = SubElement(xmlroot,"facet", {'count': "true"})
    facetfield = SubElement(facetroot,"field")
    facetfield.text = source.vs_field

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
        jsonrtn = []

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
            jsonrtn.append([rtndata['name'],rtndata['score']])

    #pprint(request.META)
    if 'HTTP_ACCEPT' in request.META:
        accept_types = request.META['HTTP_ACCEPT'].split(r', ')
        #pprint(accept_types)
        if "application/json" in accept_types:
            return HttpResponse(json.dumps(jsonrtn),content_type='application/json',status=200)
        elif "text/html" in accept_types or "*/*" in accept_types:
            return render(request,"tagsource.html",{'tagdata': rtn[root]})
        else:
            return HttpResponse("Invalid ACCEPT type",content_type='text/plain',status=405)
    return render(request,"tagsource.html",{'tagdata': rtn[root]})
    #return HttpResponse(json.dumps(rtn),content_type='application/json',status=200)

def add_data_source(request):
    if request.method != 'POST':
        return HttpResponse("Invalid method",status=400)

    f = AddSourceForm(request.POST)
    #if not f.is_valid():
    #    return HttpResponse("Form not valid",status=400)

    f.save()
    return HttpResponse("",status=204)
