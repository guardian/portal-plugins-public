from django.conf.urls.defaults import patterns, url
from views import OptInCreate, ViewMyOptins, OptInUpdate, OptInDelete, TestFunction


urlpatterns = patterns(
    'portal.plugins.gnmoptin.views',
    url(r'^$', ViewMyOptins.as_view(), name="my_optins"),
    url(r'^add/$', OptInCreate.as_view(), name='add_optins'),
    url(r'^edit/(?P<pk>\d+)$', OptInUpdate.as_view(), name='edit_optins'),
    url(r'^delete/(?P<pk>\d+)$', OptInDelete.as_view(), name='delete_optins'),
    url(r'^test/$', TestFunction.as_view(), name='test'),
)
