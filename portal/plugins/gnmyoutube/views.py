from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView, Response
import logging
import re
from forms import *
from models import *
import json
from youtube_interface import YoutubeInterface
from tasks import update_categories_list
from traceback import format_exc
#from djcelery.models.schedules import crontab
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

class YoutubeIndexView(View):
    def get(self,request):
        return render(request,'portal.plugins.gnmyoutube/index.html')


#This view displays the main admin configuration form
class YoutubeAdminView(View):
    @method_decorator(permission_required('change_settings', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(YoutubeAdminView,self).dispatch(request,*args,**kwargs)

    def get(self,request):
        clientID = ""
        privateKey=""
        fieldID = ""

        try:
            clientID = settings.objects.get(key='clientID').value
            privateKey = settings.objects.get(key='privateKey').value
            fieldID = settings.objects.get(key='fieldID').value
        except:
            pass

        f = SettingsForm(initial={'clientID': clientID, 'privateKey': privateKey, 'fieldID': fieldID})
        return render(request,'portal.plugins.gnmyoutube/admin/adminmain.html',{'settingsform': f})

    def post(self,request):
        from pprint import pprint
        from djcelery.models import CrontabSchedule,PeriodicTask
        f = SettingsForm(request.POST)

        if f.is_valid():
            cd=f.cleaned_data
            #FIXME: need to explicity overwrite existing values otherwise you get a IntegrityError
            #settings(key='clientID',value=cd['clientID']).save()
            #settings(key='privateKey',value=cd['privateKey']).save()
            #settings(key='fieldID',value=cd['fieldID']).save()

            #pprint(cd)
            (obj,created) = settings.objects.get_or_create(key='clientID',defaults={'value': cd['clientID']})
            if not created:
                obj.value = cd['clientID']
                obj.save()

            (obj,created) = settings.objects.get_or_create(key='privateKey',defaults={'value': cd['privateKey']})
            if not created:
                obj.value = cd['privateKey']
                obj.save()

            (obj,created) = settings.objects.get_or_create(key='fieldID',defaults={'value': cd['fieldID']})
            if not created:
                obj.value = cd['fieldID']
                obj.save()


            return render(request,'portal.plugins.gnmyoutube/admin/savedsettings.html')
        else:
            #this automatically includes error information associated with the relevant fields
            return render(request,'portal.plugins.gnmyoutube/admin/adminmain.html',{'settingsform': f})

#POST to this view to make a test call, to list categories
class YoutubeTestConnectionView(APIView):
    from rest_framework.parsers import JSONParser
    from rest_framework.renderers import JSONRenderer

    parser_classes = (JSONParser, )
    renderer_classes = (JSONRenderer, )

    @method_decorator(permission_required('change_settings', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(YoutubeTestConnectionView,self).dispatch(request,*args,**kwargs)
        except StandardError as e:
            return Response({'status': 'error', 'error': str(e)}, status=500)

    def post(self,request):
        from oauth2client.client import AccessTokenRefreshError, Error as OAuthError

        from pprint import pprint
        f = SettingsForm(request.POST)

        if not f.is_valid():
            #pprint(f.__dict__)
            logging.warning("Invalid form data sent to YoutubeTestConnectionView")
            logging.warning(str(f.__dict__))
            return Response({'status': 'error','errors': f.errors}, status=400)
            #return HttpResponse(json.dumps({'status': 'error','errors': f.errors}),status=400)

        cd = f.cleaned_data

        try:
            i = YoutubeInterface()
            i.authorize_pki(cd['clientID'],cd['privateKey'])
            c = i.list_categories()
        except OAuthError as e:
            return Response({'status': 'error', 'type': 'OAuth', 'error': str(e), 'info': e.__dict__},status=500)
        except StandardError as e:
            return Response({'status': 'error', 'error': str(e)}, status=500)
            #return HttpResponse(json.dumps({'status': 'error', 'error': str(e)}), status=500)

        return Response({'status': 'unknown','error': 'Still testing', 'data': c},status=200)
        #return HttpResponse(json.dumps({'status': 'unknown','error': 'Still testing', 'data': c}),status=200)


#perform actions, for testing
class YoutubeTestAction(View):
    @method_decorator(permission_required('change_settings', login_url='/authentication/login', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(YoutubeTestAction,self).dispatch(request,*args,**kwargs)

    def get(self,request,verb):
        if verb=="update_categories":
            try:
                update_categories_list()
            except Exception as e:
                return HttpResponse("{0}: {1}\n{2}".format(e.__class__,str(e),format_exc()),content_type="text/plain",status=500)
            return HttpResponse("Update categories succeeded",content_type="text/plain",status=200)
        else:
            return HttpResponse("Verb not recognised",content_type='text/plain',status=400)