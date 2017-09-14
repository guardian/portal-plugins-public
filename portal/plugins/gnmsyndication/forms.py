from django.forms import Form,ChoiceField,Select,DateField,ModelForm,ValidationError,TextInput

class TimePeriodSelector(Form):
    from datetime import date,datetime

    START_YEAR=2014

    #@staticmethod
    def month_list(self):
        for n in range(1,13):
            d=self.date(2010,n,1)
            yield (n, d.strftime("%B")) #should also convert into the server's locale

    #@staticmethod
    def year_list(self):
        d=self.datetime.now()

        for n in range(self.START_YEAR,d.year+1):
            yield (n,n)

    #selected_month = ChoiceField(choices=month_list())
    #selected_year = ChoiceField(choices=year_list())

    def __init__(self,*args,**kwargs):
        super(TimePeriodSelector,self).__init__(*args,**kwargs)

        self.fields['selected_month'] = ChoiceField(choices=self.month_list(),widget=Select(attrs={'style': 'width:100px'}))
        self.fields['selected_year'] = ChoiceField(choices=self.year_list(),widget=Select(attrs={'style': 'width:100px'}))


class DownloadReportForm(Form):
    start_date = DateField()
    end_date = DateField()


class PlatformEditForm(ModelForm):
    class Meta:
        from models import platform
        model = platform
        #fields = ['name','intention_label','uploadstatus_field',]
        # widgets = {
        #     'uploadstatus_field': TextInput(attrs={'onfocusin': "show_field_selector('id_uploadstatus_field');"}
        #                                     )
        # }
    def is_absolute(self,url):
        import urlparse
        return bool(urlparse.urlparse(url).netloc)

    def clean(self):
        cleaned_data = super(PlatformEditForm,self).clean()

        for fieldname in ['enabled_icon_url','disable_icon_url','display_icon_url']:
            if self.is_absolute(fieldname):
                self.add_error(fieldname,ValidationError('You must specify a relative URL to an image on the server'))

        return cleaned_data