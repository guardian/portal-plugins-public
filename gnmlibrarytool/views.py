from django.views.generic import View, TemplateView


class GenericAppView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(GenericAppView, self).get_context_data(**kwargs)
        #context['latest_articles'] = Article.objects.all()[:5]
        return context