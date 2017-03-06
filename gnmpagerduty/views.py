from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from models import StorageData

class ConfigAlertsView(ListView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ConfigAlertsView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/admin_list.html"

class AlertsEditView(UpdateView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AlertsEditView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/edit.html"
    success_url = reverse_lazy('gnmpagerduty_admin')

class AlertsDeleteView(DeleteView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AlertsDeleteView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/delete.html"
    success_url = reverse_lazy('gnmpagerduty_admin')

class AlertsCreateView(CreateView):
    @method_decorator(permission_required('change_storage_alerts', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AlertsCreateView,self).dispatch(request,*args,**kwargs)
    model = StorageData
    template_name = "gnmpagerduty/edit.html"
    success_url = reverse_lazy('gnmpagerduty_admin')