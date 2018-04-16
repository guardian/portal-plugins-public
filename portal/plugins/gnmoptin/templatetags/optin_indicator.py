from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter("optin_indicator")
def optin_indicator(value):
    if value:
        return mark_safe("<span><i class=\"fa fa-lightbulb-o\" style=\"color: green; margin-right:0.5em; margin-left:0.25em\"></i>Opted In</span>")
    else:
        return mark_safe("<span><i class=\"fa fa-lightbulb-o\" style=\"color: grey; margin-right:0.5em; margin-left:0.25em\"></i>Opted Out</span>")