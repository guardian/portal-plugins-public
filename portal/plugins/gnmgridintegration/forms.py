from django import forms


class ConfigForm(forms.Form):
    is_enabled = forms.BooleanField(widget=forms.CheckboxInput)
