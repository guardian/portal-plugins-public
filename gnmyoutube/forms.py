from django.forms import ModelForm,Form,ModelChoiceField,CharField,TimeField,TextInput,Textarea,ValidationError


class SettingsForm(Form):
    clientID = CharField(max_length=512,label="Google Client email")
    privateKey = CharField(max_length=32768,widget=Textarea,label="Private Key contents")
    fieldID = CharField(max_length=512,label="Vidispine ID of YouTube categories field")
    #updateCategoriesTime = TimeField(label="Run daily category update at")

    def clean_fieldID(self):
        import httplib2
        from plugin import make_vidispine_request
        from django.conf import settings
        import logging
        from pprint import pprint

        current_value = self.cleaned_data['fieldID']

        uri = "/API/metadata-field/{2}".format(settings.VIDISPINE_URL,settings.VIDISPINE_PORT,current_value)

        h = httplib2.Http()
        (headers,content) = make_vidispine_request(h,"GET",uri,"",{'Accept': 'application/xml'})
        pprint(headers)

        if int(headers['status']) == 404:
            raise ValidationError("{0} is not a valid Vidispine field".format(current_value))

        if int(headers['status'])<200 or int(headers['status'])>299:
            raise ValidationError("Vidispine error - {0}".format(content))

        logging.debug("Field information: {0}".format(content))

        return current_value