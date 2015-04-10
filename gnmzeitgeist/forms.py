from django.forms import Form,ModelChoiceField
from models import datasource


class DataSourceForm(Form):
    source = ModelChoiceField(queryset=datasource.objects.all())
