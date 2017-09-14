from django.conf.urls.defaults import patterns, url
import views
#from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portal.plugins.portal.plugins.gnmpropagation.views',
    url(r'^p/$', views.p, name="request"),
)
