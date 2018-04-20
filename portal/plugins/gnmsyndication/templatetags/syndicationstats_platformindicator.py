from django import template
from django.utils.safestring import mark_safe
import portal.plugins.gnmsyndication.models as models
import logging

register = template.Library()


@register.filter("platformindicatortwo")
def platformIndicator(value):
    logging.debug("platformindicator: upload intentions: {0}".format(value))
    if not isinstance(value,list):
        value = [value]

    lowered_values = []
    for v in value:
        lowered_values.append(v.lower())

    rtn = u""

    for p in models.platform.objects.all():
        if p.intention_label in lowered_values:
            rtn += u"<img class=\"tooltip_icon inline_medium_icon\" src=\"{0}\" alt=\"{1} enabled\">".format(p.enabled_icon_url,p.name)
        else:
            rtn += u"<img class=\"tooltip_icon inline_medium_icon\" src=\"{0}\" alt=\"{1} disabled\">".format(p.disable_icon_url,p.name)

    return mark_safe(rtn)