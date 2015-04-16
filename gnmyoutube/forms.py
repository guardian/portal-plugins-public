from django.forms import ModelForm,Form,ModelChoiceField,CharField,TextInput,Textarea


class SettingsForm(Form):
    clientID = CharField(max_length=512,label="Google Client ID")
    privateKey = CharField(max_length=32768,widget=Textarea,label="Private Key contents")