from django.views.generic import View, TemplateView

class MainAppView(TemplateView):
    from .forms import ShowSearchForm
    template_name = "gnmlibrarytool/index.html"

    def get_context_data(self, **kwargs):
        context = super(MainAppView, self).get_context_data(**kwargs)
        context['search_form'] = self.ShowSearchForm()
        #context['latest_articles'] = Article.objects.all()[:5]
        return context


class LibraryListView(View):

    def get(self,request):
        from .VSLibrary import VSLibrary, VSLibraryCollection, HttpError
        from django.http import HttpResponse
        import json
        onlyAutoRefresh = None
        if 'autoRefresh' in request.GET:
            if request.GET['autoRefresh'].downcase() == "true":
                onlyAutoRefresh = True
            else:
                onlyAutoRefresh = False

        from django.conf import settings
        libraries = VSLibraryCollection(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                                        username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD)

        rtn = []
        for libname in libraries.scan(autoRefresh=onlyAutoRefresh):
            l=VSLibrary(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                        username=settings.VIDISPINE_USERNAME,password=settings.VIDISPINE_PASSWORD)

            rtn.append({'id': libname, 'hits': l.get_hits(libname)})
        return HttpResponse(content=json.dumps(rtn),content_type='application/json', status=200)
