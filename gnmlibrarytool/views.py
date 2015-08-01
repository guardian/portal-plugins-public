from django.views.generic import View, TemplateView
from .forms import *


class MainAppView(TemplateView):
    template_name = "gnmlibrarytool/index.html"

    def get_context_data(self, **kwargs):
        context = super(MainAppView, self).get_context_data(**kwargs)
        context['search_form'] = ShowSearchForm()
        context['welcome'] = "This is a welcome message from python"
        #context['latest_articles'] = Article.objects.all()[:5]
        return context