from django.forms import Form,ChoiceField,Select

class TimePeriodSelector(Form):
    from datetime import date,datetime

    START_YEAR=2014

    #@staticmethod
    def month_list(self):
        for n in range(1,12):
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