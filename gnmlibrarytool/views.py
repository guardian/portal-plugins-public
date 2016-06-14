from django.views.generic import View, TemplateView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, XMLRenderer
from vsmixin import HttpError, VSMixin
from models import LibraryNickname, LibraryNicknameSerializer
import logging

logger = logging.getLogger(__name__)


class DiagramMainView(TemplateView):
    template_name = 'gnmlibrarytool/diagram.html'


class RuleDiagramDataView(VSMixin, APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    def __init__(self,*args,**kwargs):
        super(RuleDiagramDataView,self).__init__(*args,**kwargs)
        import re

        self._xtract_namespace = re.compile(r'^{[^}]*}')

    def get_field_name(self,elem):
        try:
            return elem.find('{0}name'.format(self._ns)).text
        except StandardError as e:
            return "(not found)"

    def process_field(self, elem):
        rtn = {
            'type': 'field',
            'name': self.get_field_name(elem),
            'values': []
        }
        for val in elem.findall('{0}value'.format(self._ns)):
            rtn['values'].append(val.text)

        return rtn

    def process_operator(self, elem):
        return {
            'type': 'operator',
            'operation': elem.attrib['operation'],
            'members': self.search_diagram_data(elem)
        }

    def search_diagram_data(self, query_doc):
        """
        :param query_doc: ElementTree representation of the query document as returned by VSLibrary
        :return:
        """
        batch = []
        for child_node in query_doc:
            real_name = self._xtract_namespace.sub('',child_node.tag)
            if real_name == 'operator':
                batch.append(self.process_operator(child_node))
            elif real_name == 'field':
                batch.append(self.process_field(child_node))
        return batch

    def _xml_get(self, tagname, doc, default='(not found)'):
        try:
            return doc.find('{0}{1}'.format(self._ns,tagname)).text
        except StandardError:
            return default

    def storage_list(self, rule_doc):
        rtn = []
        for groupnode in rule_doc.findall('{0}group'.format(self._ns)):
            rtn.append(groupnode.text)
        for stornode in rule_doc.findall('{0}storage'.format(self._ns)):
            rtn.append(stornode.text)

        return rtn

    def rule_diagram_data(self, rule_doc):
        rtn = {}
        for tag_node in rule_doc.findall('{0}tag'.format(self._ns)):
            rtn[tag_node.attrib['id']] = {
                'count': int(self._xml_get('storageCount', tag_node, default="-1")),
                'precedence': self._xml_get('precedence', tag_node, default='(unknown)'),
                'include': self.storage_list(tag_node),
                'exclude': []
            }
            try:
                rtn[tag_node.attrib['id']]['exclude'] = self.storage_list(tag_node.find('{0}not'.format(self._ns)))
            except StandardError as e:
                logger.warning(e)
        return rtn

    def get(self, response, lib=None):
        from .VSLibrary import VSLibrary, HttpError
        from models import LibraryNickname
        from django.conf import settings
        from traceback import format_exc
        import memcache

        mc = memcache.Client([settings.CACHE_LOCATION])

        l = VSLibrary(url=self.vidispine_url,port=self.vidispine_port,
                      username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD,cache=mc)

        #try:
        l.populate(lib)
        #except HttpError as e:
        #    return Response({'status': 'error', 'error': str(e), 'trace': format_exc()}, status=400)

        rtn = {
            'id': lib,
            'hits': l.get_hits(lib),
            'nickname': None,
            'query': self.search_diagram_data(l.query),
            'rules': self.rule_diagram_data(l.storagerule)
        }

        try:
            nick_data = LibraryNickname.objects.get(library_id=lib)
            rtn['nickname'] = nick_data.nickname
        except LibraryNickname.DoesNotExist:
            nick_data = None

        return Response({'status': 'ok','data': rtn})


class NicknameQueryViewset(viewsets.ReadOnlyModelViewSet):
    queryset = LibraryNickname.objects.all().order_by('nickname')
    serializer_class = LibraryNicknameSerializer

    def get_queryset(self):
        from itertools import chain

        qs = super(NicknameQueryViewset, self).get_queryset()

        #if the rules engine plugin is available, then add in what's known there...
        try:
            from portal.plugins.rulesengine.models import DistributionMetadataRule

            portal_rules = DistributionMetadataRule.objects.all()

            qs = list(chain(qs, map(lambda x: {'library_id': x.vs_id, 'nickname': x.name}, portal_rules)))
        except ImportError as e:
            pass
        return qs


class MainAppView(TemplateView):
    from .forms import ShowSearchForm
    template_name = "gnmlibrarytool/index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request.GET, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, getargs, **kwargs):
        import memcache
        from .VSLibrary import VSLibrary, HttpError
        from .forms import ConfigurationForm
        from django.conf import settings

        mc = memcache.Client([settings.CACHE_LOCATION])
        context = super(MainAppView, self).get_context_data(**kwargs)

        initial_search_form = {}
        if 'only_named' in getargs:
            if getargs['only_named']=="1" or getargs['only_named']=="true":
                initial_search_form['only_named'] = True
        if 'only_with_storage_rules' in getargs:
            if getargs['only_with_storage_rules']=="1" or getargs['only_with_storage_rules']=="true":
                initial_search_form['only_with_storage_rules'] = True
        if 'only_auto_refreshing' in getargs:
            if getargs['only_auto_refreshing']=="1" or getargs['only_auto_refreshing']=="true":
                initial_search_form['only_auto_refreshing'] = True

        context['search_form'] = self.ShowSearchForm(initial=initial_search_form)

        #context['debug_notes'] = kwargs
        l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                      username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD,cache=mc)
        try:
            l.populate(kwargs['lib'])
            context['configuration_form'] = ConfigurationForm(l)
        except HttpError as e:
            context['configuration_form_error'] = e.__unicode__()
        except KeyError:
            pass

        #context['latest_articles'] = Article.objects.all()[:5]
        return context

    def post(self, request, *args, **kwargs):
        from .forms import ConfigurationForm
        from .VSLibrary import VSLibrary, HttpError
        from .models import LibraryNickname
        from django.conf import settings
        from xml.parsers.expat import ExpatError
        #from xml.etree.ElementTree import ParseError
        import memcache
        from django.shortcuts import render

        mc = memcache.Client([settings.CACHE_LOCATION])

        f = ConfigurationForm(None, request.POST)
        if f.is_valid():
            l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                      username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD, cache=mc)
            l.cache_timeout = 3600
            cd = f.cleaned_data
            context = {'search_form': self.ShowSearchForm() }

            try:
                #update the internal nickname
                try:
                    n = LibraryNickname.objects.get(library_id=kwargs['lib'])
                except LibraryNickname.DoesNotExist:
                    n = LibraryNickname()
                    n.library_id = kwargs['lib']
                n.nickname = cd['nickname']
                n.save()

                l.populate(kwargs['lib'])
                l.autoRefresh=cd['auto_refresh']
                l.updateMode=cd['update_mode']
                l.query=cd['search_definition']
                l.saveSettings()
                context['configuration_form_error'] = "Your update has been saved successfully"
            except HttpError as e:
                context['configuration_form_error'] = "Error saving to vidispine: %s" % e.__unicode__()
            except ExpatError as e:
                 context['configuration_form_error'] = "Query is not valid XML: %s" % e
            return render(request, self.template_name, context)

        else:
            print "form not valid"
            return render(request,self.template_name,self.get_context_data(**kwargs))


class ConfigurationFormProcessorView(View):
    def __init__(self,*args,**kwargs):
        import memcache
        from django.conf import settings
        super(ConfigurationFormProcessorView, self).__init__(*args,**kwargs)
        self._mc = memcache.Client([settings.CACHE_LOCATION])

    def handle_action(self,request,cleaned_data,*args,**kwargs):
        from django.http import HttpResponse

        return HttpResponse(content='not implemented',status=500,content_type='text/plain')

    def post(self, request, *args, **kwargs):
        from .forms import ConfigurationForm
        from .VSLibrary import VSLibrary, HttpError, VSLibraryCollection
        from django.http import HttpResponse
        from django.conf import settings
        import json

        f = ConfigurationForm(None, request.POST)
        if f.is_valid():
            cd = f.cleaned_data
            try:
                return self.handle_action(request,cd,*args,**kwargs)

            except HttpError as e:
                return HttpResponse(content=json.dumps({'status': 'error', 'message': "Error updating vidispine: %s" % e.__unicode__()}),
                                    content_type='application/json', status=500)
            except ValueError as e:
                return HttpResponse(content=json.dumps({'status': 'error', 'message': "Invalid parameters: %s" % e.__unicode__()}),
                                    content_type='application/json', status=400)
        else:
            return HttpResponse(content=json.dumps({'status': 'error', 'message': "Form not valid", 'details': f.errors}),
                                content_type='application/json', status=400)


class DeleteLibraryView(ConfigurationFormProcessorView):
    def handle_action(self,request,cleaned_data,*args,**kwargs):
        from .VSLibrary import VSLibrary,VSLibraryCollection
        from django.conf import settings
        from django.http import HttpResponse
        from .models import LibraryNickname
        import json

        l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
        username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD, cache=self._mc)
        l.cache_timeout = 3600

        l.populate(cleaned_data['library_id'])
        print "attempting to delete %s" % cleaned_data['library_id']
        l.delete()
        #now it's deleted, invalidate the cache for the library collection list so it stops showing up
        libraries = VSLibraryCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                        username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD,
                        cache=self._mc)
        libraries.cache_invalidate()

        try:
            n=LibraryNickname.objects.get(library_id=cleaned_data['library_id'])
            n.delete()
        except LibraryNickname.DoesNotExist:
            pass

        return HttpResponse(content=json.dumps({'status': 'success', 'action': 'deleted', 'vsid': l.vsid}),
                            content_type='application/json', status=200)


class SaveStorageRuleView(ConfigurationFormProcessorView):
    def handle_action(self, request, cleaned_data, *args, **kwargs):
        from .VSLibrary import VSLibrary,VSLibraryCollection
        from django.conf import settings
        from django.http import HttpResponse
        import xml.etree.ElementTree as ET
        from xml.parsers.expat import ExpatError
        import json

        l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
        username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD, cache=self._mc)
        l.cache_timeout = 3600

        l.populate(cleaned_data['library_id'])
        try:
            doc = ET.fromstring(cleaned_data['storage_rule_definition'])
            print "storage rule to set: %s" % ET.tostring(doc,"UTF-8")

            l.storagerule = doc
            l.saveStorageRule() #HttpErrors are caught by the superclass. This call performs cache invalidation on the object.
        except ExpatError as e:
            return HttpResponse(content=json.dumps({'status': 'error', 'vsid': l.vsid, 'message': "Storage rule is not valid XML",
                                                    'detail': e.__unicode__()}),
                                content_type='application/json', status=400)

        return HttpResponse(content=json.dumps({'status': 'success', 'action': 'updated', 'vsid': l.vsid}),
                            content_type='application/json', status=200)

class DeleteStorageRuleView(ConfigurationFormProcessorView):
    def handle_action(self,request,cleaned_data,*args,**kwargs):
        from .VSLibrary import VSLibrary,VSLibraryCollection
        from django.conf import settings

        l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
        username=settings.VIDISPINE_USERNAME, password=settings.VIDISPINE_PASSWORD, cache=self._mc)
        l.cache_timeout = 3600

        l.populate(cleaned_data['library_id'])
        l.deleteStorageRule()

class CreateLibraryView(View):
    def put(self,request):
        from .VSLibrary import VSLibrary,VSLibraryCollection,HttpError
        from django.conf import settings
        from django.http import HttpResponseRedirect,HttpResponse
        from django.core.urlresolvers import reverse
        import memcache
        import traceback
        import json

        l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                    username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD)
        try:
            l.create_new()
        except HttpError as e:
            print e.__unicode__()
            return HttpResponse(content='Unable to create library: {0}\n{1}'.format(e.__unicode__(),traceback.format_exc()),content_type='text/plain',status=500)

        mc = memcache.Client([settings.CACHE_LOCATION])
        libraries = VSLibraryCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                        username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD,
                                        cache=mc)
        libraries.cache_invalidate()

        return HttpResponse(content=json.dumps({'status': 'success', 'action': 'created', 'vsid': l.vsid}),
                            content_type='application/json',status=200)

        #return HttpResponseRedirect(reverse('libtool_editor',kwargs={'lib': l.vsid}))


class LibraryListView(View):
    def scan_page(self,libraries,page,onlyNamed=None,onlyAutoRefresh=None,cache=None):
        from portal.plugins.rulesengine.models import DistributionMetadataRule
        import logging
        from .VSLibrary import VSLibrary,HttpError
        from django.conf import settings
        from .models import LibraryNickname

        rtn = []

        for libname in libraries.scan(page=page, autoRefresh=onlyAutoRefresh):
            nickname = ""
            #is it a Portal rule?
            try:
                n = DistributionMetadataRule.objects.get(vs_id=libname)
                nickname = n.name
            except DistributionMetadataRule.DoesNotExist:
                pass
            #do we know about it?
            try:
                n = LibraryNickname.objects.get(library_id=libname)
                nickname = n.nickname
            except LibraryNickname.DoesNotExist:
                pass

            try:
                l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                            username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD,cache=cache)
                l.cache_timeout = 3600  #cache library definitions for 1hr
                if onlyNamed is None:
                    rtn.append({'id': libname, 'hits': l.get_hits(libname), 'nickname': nickname})
                elif onlyNamed:
                    if nickname != "": rtn.append({'id': libname, 'hits': l.get_hits(libname), 'nickname': nickname})
                else:
                    if nickname == "": rtn.append({'id': libname, 'hits': l.get_hits(libname), 'nickname': nickname})

            except HttpError as e:
                if e.status!=404:
                    raise e #re-raise exception to outer loop, we don't know what happened
                logging.warning(e.__unicode__())
        return rtn

    def get(self,request):
        from .VSLibrary import VSLibrary, VSLibraryCollection, HttpError
        from django.http import HttpResponse
        import json
        import logging
        import memcache
        from django.conf import settings
        from .models import LibraryNickname

        onlyAutoRefresh = None
        if 'autoRefresh' in request.GET:
            if request.GET['autoRefresh'].lower() == "true":
                onlyAutoRefresh = True
            else:
                onlyAutoRefresh = False

        onlyNamed = None
        if 'onlyNamed' in request.GET:
            if request.GET['onlyNamed'].lower() == "true":
                onlyNamed = True
            else:
                onlyNamed = False

        mc = memcache.Client([settings.CACHE_LOCATION])

        libraries = VSLibraryCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                        username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD,
                                        cache=mc)

        if 's' in request.GET:
            libraries.page_size = int(request.GET['s'])
        page = 0
        if 'p' in request.GET:
            page = int(request.GET['p'])

        rtn = []
        try:
            n = 0
            while len(rtn) < libraries.page_size:
                rtn += self.scan_page(libraries,page+n,onlyNamed=onlyNamed,onlyAutoRefresh=onlyAutoRefresh,cache=mc)
                n+=1
                if n > libraries.page_count: break

            return HttpResponse(content=json.dumps({'status': 'ok','total': libraries.count, 'pages': libraries.page_count,
                                                    'results': rtn}),content_type='application/json', status=200)
        except HttpError as e:
            return HttpResponse(content=json.dumps({'status': 'error', 'error': e.__unicode__()}), content_type='application/json', status=500)


class StorageRuleInfoView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer, XMLRenderer, )

    def get(self,request,itemid):
        from gnmvidispine.vs_item import VSItem
        from django.conf import settings
        import traceback
        try:
            itemref = VSItem(url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD,
                             run_as=request.user.username)

            itemref.populate(itemid,specificFields=['title'])

            rtn = []
            for s in itemref.shapes():
                info = {"shapetag": s.tag(), "shapeid": s.name, "rules": map(lambda x: x.as_dict(), s.storage_rules().rules()) }
                rtn.append(info)

            return Response(rtn, status=200)

        except Exception as e:
            return Response({'status': 'error', 'error': str(e), 'trace': traceback.format_exc()})