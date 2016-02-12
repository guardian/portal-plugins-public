from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse_lazy
import views
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.gnmpropagation.views',
    url(r'^p/$', views.p, name="request"),
)
