from django.forms import Form,ModelChoiceField,ModelForm
from models import datasource


class DataSourceForm(Form):
    source = ModelChoiceField(queryset=datasource.objects.all(),empty_label=None,to_field_name='name')


class AddSourceForm(ModelForm):
    class Meta:
        model = datasource
        fields = ['name','vs_field','value_mapping_id']
