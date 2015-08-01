from django.forms import *


class ShowSearchForm(Form):
    only_named = BooleanField(required=False)
    only_with_storage_rules = BooleanField(required=False)
    only_auto_refreshing = BooleanField(required=False)

