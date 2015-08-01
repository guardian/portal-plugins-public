from django.forms import *


class ShowSearchForm(Form):
    only_named = BooleanField()
    only_with_storage_rules = BooleanField()
    only_auto_refreshing = BooleanField()

