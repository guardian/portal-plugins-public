from django.views.generic import View, TemplateView

class MainAppView(TemplateView):
    from .forms import ShowSearchForm
    template_name = "gnmlibrarytool/index.html"

    def get_context_data(self, **kwargs):
        import memcache
        from .VSLibrary import VSLibrary, HttpError
        from .forms import ConfigurationForm
        from django.conf import settings

        mc = memcache.Client([settings.CACHE_LOCATION])
        context = super(MainAppView, self).get_context_data(**kwargs)
        context['search_form'] = self.ShowSearchForm()
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
        from django.conf import settings
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
                l.populate(kwargs['lib'])
                l.autoRefresh=cd['auto_refresh']
                l.updateMode=cd['update_mode']
                l.query=cd['search_definition']
                l.saveSettings()
                context['configuration_form_error'] = "Your update has been saved successfully"
            except HttpError as e:
                context['configuration_form_error'] = "Error saving to vidispine: %s" % e
            #except ParseError as e:
            #    context['configuration_form_error'] = "Query is not valid XML: %s" % e
            return render(request, self.template_name, context)

        else:
            print "form not valid"
            return render(request,self.template_name,self.get_context_data(**kwargs))


class CreateLibraryView(View):
    def put(self,request):
        from .VSLibrary import VSLibrary,VSLibraryCollection,HttpError
        from django.conf import settings
        from django.http import HttpResponseRedirect
        from django.core.urlresolvers import reverse
        import memcache

        l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                    username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD)
        l.create_new()

        mc = memcache.Client([settings.CACHE_LOCATION])
        libraries = VSLibraryCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                        username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD,
                                        cache=mc)
        libraries.cache_invalidate()

        return HttpResponseRedirect(reverse('libtool_editor',kwargs={'lib': l.vsid}))

class LibraryListView(View):

    def get(self,request):
        from .VSLibrary import VSLibrary, VSLibraryCollection, HttpError
        from django.http import HttpResponse
        import json
        import logging
        import memcache
        from django.conf import settings

        onlyAutoRefresh = None
        if 'autoRefresh' in request.GET:
            if request.GET['autoRefresh'].lower() == "true":
                onlyAutoRefresh = True
            else:
                onlyAutoRefresh = False

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
            for libname in libraries.scan(page=page, autoRefresh=onlyAutoRefresh):
                try:
                    l = VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD,cache=mc)
                    l.cache_timeout = 3600  #cache library definitions for 1hr
                    rtn.append({'id': libname, 'hits': l.get_hits(libname)})
                except HttpError as e:
                    if e.status!=404:
                        raise e #re-raise exception to outer loop, we don't know what happened
                    logging.warning(e.__unicode__())

            return HttpResponse(content=json.dumps({'status': 'ok','total': libraries.count, 'pages': libraries.page_count,
                                                    'results': rtn}),content_type='application/json', status=200)
        except HttpError as e:
            return HttpResponse(content=json.dumps({'status': 'error', 'error': e.__unicode__()}), content_type='application/json', status=500)