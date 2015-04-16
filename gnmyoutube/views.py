from portal.generic.baseviews import ClassView
from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render
import logging
import re
from forms import *
from models import *

class YoutubeIndexView(View):
    def get(self,request):
        return render(request,'gnmyoutube/index.html')

class YoutubeAdminView(View):
    def get(self,request):
        f = SettingsForm()
        return render(request,'gnmyoutube/admin/adminmain.html',{'settingsform': f})

    def post(self,request):
        f = SettingsForm(request.POST)

        if f.is_valid():
            cd=f.cleaned_data
            settings(key='clientID',value=cd['clientID']).save()
            settings(key='privateKey',value=cd['privateKey']).save()
            return render(request,'gnmyoutube/admin/savedsettings.html')
        else:
            return render(request,'gnmyoutube/admin/adminmain.html',{'settingsform': f})


class YoutubeTestConnectionView(View):
    def post(self,request):
        raise StandardError("Not yet implemented")