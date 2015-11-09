#https://docs.djangoproject.com/en/1.7/howto/custom-template-tags/

from django import template
from django.utils.safestring import mark_safe
import portal.plugins.gnmsyndication.models as models
import logging

register = template.Library()

@register.filter("jobstatus_formatter")
def jobStatusFormatter(value):
    classname = value.lower()

    return "<span class=\"{0}\">{1}</span>".format(classname,value)

@register.filter("syndicationstatus_icon")
def syndicationStatusFormatter(value):
    icon = None
    iconpath = '/sitemedia/img/gnm/'

    if(value=='Upload Succeeded'):
        icon = iconpath + 'published.png'
    elif(value=='Do Not Send'):
        icon = iconpath + 'unpublished.png'
    elif(value=='Upload Failed'):
        icon = iconpath + 'severity_3.png'
    elif(value=='Ready to Upload'):
        icon = iconpath + 'ready_to_publish.png'
    elif(value=='Upload in Progress'):
        icon = iconpath + 'ready_to_publish.png'
    elif(value=='Transcode in Progress'):
        icon = iconpath + 'ready_to_publish.png'
    elif(value=='Not Ready'):
        icon = iconpath + 'draft.png'

    if icon is not None:
        iconstr = "<img src=\"{0}\" alt=\"{1}\">".format(icon,value)
    else:
        iconstr = ""

    return mark_safe(u"<span class=\"{0}\">{1}&nbsp;&nbsp;{2}</span>".format(value.lower(),iconstr,value))

@register.filter("platformindicator")
def platformIndicator(value):
    #if isinstance(value,list):
    #    return " | ".join(value)
    #else:
    #    return value

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

@register.filter("pacformindicator")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'

    icon_url = ""
    if value=="valid":
        icon_url = iconpath + 'severity_0.png'
    elif value=="processing":
        icon_url = iconpath + 'severity_1.png'
    elif value=="invalid":
        icon_url = iconpath + 'severity_3.png'
    elif value=="missing":
        icon_url = iconpath + 'severity_2.png'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,value))

@register.filter("automationindicator")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'

    icon_url = ""

    text = "default"

    if '"status": "ok"' in value:
        icon_url = iconpath + 'severity_0.png'
        text = 'Okay'
    elif value=="":
        icon_url = iconpath + 'severity_2.png'
        text = 'Not&nbsp;set'
    else:
        icon_url = iconpath + 'severity_3.png'
        text = 'Failed'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("msinfo")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    if '"mainstreamsyndication": "allow"' in value:
        icon_url = iconpath + 'severity_0.png'
        text = 'Allow'
    elif '"mainstreamsyndication": "forbid"' in value:
        icon_url = iconpath + 'severity_3.png'
        text = 'Forbid'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("dminfo")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    if '"dailymotion": "allow"' in value:
        icon_url = iconpath + 'severity_0.png'
        text = 'Allow'
    elif '"dailymotion": "forbid"' in value:
        icon_url = iconpath + 'severity_3.png'
        text = 'Forbid'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("ytinfo")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    if '"youtube": "allow"' in value:
        icon_url = iconpath + 'severity_0.png'
        text = 'Allow'
    elif '"youtube": "forbid"' in value:
        icon_url = iconpath + 'severity_3.png'
        text = 'Forbid'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("fbinfo")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    if '"facebook": "allow"' in value:
        icon_url = iconpath + 'severity_0.png'
        text = 'Allow'
    elif '"facebook": "forbid"' in value:
        icon_url = iconpath + 'severity_3.png'
        text = 'Forbid'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("sinfo")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    if '"spotify": "allow"' in value:
        icon_url = iconpath + 'severity_0.png'
        text = 'Allow'
    elif '"spotify": "forbid"' in value:
        icon_url = iconpath + 'severity_3.png'
        text = 'Forbid'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("automationerrors")
def pacformIndicator(value):

    text = ""

    if '"status": "ok"' in value:
        text = 'None'
    elif "Matching rule was invalid for response" in value:
        text = 'Matching rule was invalid for response'
    elif "Invalid master" in value:
        text = 'Invalid master'
    elif value=="":
        text = 'Unknown'
    else:
        text = 'Unknown'

    return mark_safe(text)