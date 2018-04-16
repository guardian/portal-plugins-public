from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView
from models import UserOptIn
from django.core.urlresolvers import reverse_lazy
from forms import OptInForm
from functions import userfeature


class ViewMyOptins(ListView):
    template_name = "gnmoptin/my_optins.html"

    model = UserOptIn

    def get_queryset(self):
        return UserOptIn.objects.filter(user=self.request.user)


class OptInCreate(CreateView):
    model = UserOptIn
    fields = ['feature']
    template_name = "gnmoptin/add_optins.html"
    success_url = reverse_lazy("my_optins")
    form_class = OptInForm

    def get_form_kwargs(self):
        kwargs = super(OptInCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['enabled'] = True
        return kwargs


class OptInUpdate(UpdateView):
    model = UserOptIn
    template_name = "gnmoptin/change_optins.html"
    success_url = reverse_lazy("my_optins")


class OptInDelete(DeleteView):
    model = UserOptIn
    template_name = "gnmoptin/delete_optins.html"
    success_url = reverse_lazy("my_optins")


class TestFunction(TemplateView):
    template_name = "gnmoptin/test.html"

    def get(self, request, *args, **kwargs):
        test_data = userfeature(self.request.user, self.request.GET['test'])
        print test_data
