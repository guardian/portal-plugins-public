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
    elif('Not Ready' in value):
        icon = iconpath + 'draft.png'

    if icon is not None:
        iconstr = "<img src=\"{0}\" alt=\"{1}\">".format(icon,value)
    else:
        iconstr = ""

    if ('Not Ready' in value) & (value != 'Not Ready'):
        textforpassing = value
        return mark_safe(u"<span class=\"{0}\">{1}&nbsp;&nbsp;{2}</span>".format(textforpassing,iconstr,'Not Ready'))
    else:
        textforpassing = value.lower()

    if value == 'Not Ready':
        textforpassing = value.lower()

    return mark_safe(u"<span class=\"{0}\">{1}&nbsp;&nbsp;{2}</span>".format(textforpassing,iconstr,value))


@register.filter("pacformindicator")
def pacformIndicator(value):
    iconpath = '/sitemedia/img/gnm/'

    text = ""
    icon_url = ""
    if value=="valid":
        icon_url = iconpath + 'severity_0.png'
        text = "valid"
    elif value=="processing":
        icon_url = iconpath + 'severity_1.png'
        text = "processing"
    elif value=="invalid":
        icon_url = iconpath + 'severity_3.png'
        text = "invalid"
    elif value=="missing":
        icon_url = iconpath + 'severity_2.png'
        text = "missing"
    else:
        icon_url = iconpath + 'severity_1.png'
        text = "unknown"

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("automationindicator")
def automationIndicator(value):
    iconpath = '/sitemedia/img/gnm/'

    icon_url = ""

    text = "default"

    try:
        if '"status": "ok"' in value:
            icon_url = iconpath + 'severity_0.png'
            text = 'Okay'
        elif value=="":
            icon_url = iconpath + 'severity_2.png'
            text = 'Not&nbsp;set'
        else:
            icon_url = iconpath + 'severity_3.png'
            text = 'Failed'
    except Exception as e:
        logging.error("automationIndicator could not get automation status from '{0}'".format(value))
        icon_url = iconpath + 'severity_3.png'
        text = 'Internal error'
    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("msinfo")
def msInfo(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    try:
        if '"mainstreamsyndication": "allow"' in value:
            icon_url = iconpath + 'severity_0.png'
            text = 'Allow'
        elif '"mainstreamsyndication": "forbid"' in value:
            icon_url = iconpath + 'severity_3.png'
            text = 'Forbid'
    except Exception as e:
        logging.error("automationIndicator could not get automation status from '{0}'".format(value))
        icon_url = iconpath + 'severity_3.png'
        text = 'Internal error'
    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("dminfo")
def dmInfo(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    try:
        if '"dailymotion": "allow"' in value:
            icon_url = iconpath + 'severity_0.png'
            text = 'Allow'
        elif '"dailymotion": "forbid"' in value:
            icon_url = iconpath + 'severity_3.png'
            text = 'Forbid'
    except Exception as e:
        logging.error("dmInfo could not get automation status from '{0}'".format(value))
        icon_url = iconpath + 'severity_3.png'
        text = 'Internal error'

    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))


@register.filter("ytinfo")
def ytInfo(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    try:
        if '"youtube": "allow"' in value:
            icon_url = iconpath + 'severity_0.png'
            text = 'Allow'
        elif '"youtube": "forbid"' in value:
            icon_url = iconpath + 'severity_3.png'
            text = 'Forbid'
    except Exception as e:
        logging.error("ytInfo could not get automation status from '{0}'".format(value))
        icon_url = iconpath + 'severity_3.png'
        text = 'Internal error'
    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("fbinfo")
def fbInfo(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    try:
        if '"facebook": "allow"' in value:
            icon_url = iconpath + 'severity_0.png'
            text = 'Allow'
        elif '"facebook": "forbid"' in value:
            icon_url = iconpath + 'severity_3.png'
            text = 'Forbid'
    except Exception as e:
        logging.error("fbInfo could not get automation status from '{0}'".format(value))
        icon_url = iconpath + 'severity_3.png'
        text = 'Internal error'
    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("sinfo")
def sInfo(value):
    iconpath = '/sitemedia/img/gnm/'
    icon_url = iconpath + 'severity_1.png'
    text = "n/a"

    try:
        if '"spotify": "allow"' in value:
            icon_url = iconpath + 'severity_0.png'
            text = 'Allow'
        elif '"spotify": "forbid"' in value:
            icon_url = iconpath + 'severity_3.png'
            text = 'Forbid'
    except Exception as e:
        logging.error("sInfo could not get automation status from '{0}'".format(value))
        icon_url = iconpath + 'severity_3.png'
        text = 'Internal error'
    return mark_safe(u"<img class=\"inline_icon\" src=\"{0}\">{1}".format(icon_url,text))

@register.filter("automationerrors")
def automationErrors(value):

    import json

    text = ""

    try:
        if '"status": "ok"' in value:
            text = 'None'
        elif '"status": "error"' in value:
            try:
                jdata = json.loads(value)
            except:
                return 'Unknown'
            try:
                jdata2 = jdata['error']
            except:
                return 'Unknown'
            try:
                return jdata2['message']
            except:
                return 'Unknown'

        elif value=="":
            text = 'Unknown'
        else:
            text = 'Unknown'
    except Exception as e:
        text = "automationErrors could not get automation status from '{0}'".format(value)
        logging.error(text)

    return mark_safe(text)

@register.filter("ruleinfo")
def ruleInfo(value):

    import json

    if value != "":
        try:
            jdata = json.loads(value)
        except:
            return 'None'
        try:
            jdata2 = jdata['matched']
        except:
            return 'None'
        try:
            return jdata2['rule']
        except:
            return 'None'
    else:
        return 'None'

@register.filter("displaydate")
def displayDate(value):

    import time
    import re
    if not isinstance(value, basestring):
        logging.warning("displayDate expects a string, got a type {0} ({1})".format(value.__class__.__name__, value))
        return "n/a"

    if re.match("\d", value) is not None:

        try:
            inputdate = time.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except:
            inputdate = time.strptime(value, "%Y-%m-%dT%H:%M:%S")

        try:
            finisheddate = time.strftime("%H:%M:%S %d/%m/%Y", inputdate).lstrip("0").replace("/0", "/").replace(" 0", " ")
        except:
            return value
        if finisheddate[0] == ':':
            finisheddate = '0'+finisheddate
        return finisheddate
    else:
        return ""

@register.filter("displaydateinfo")
def displayDateInfo(value):

    import time
    import re
    if not isinstance(value, basestring):
        logging.warning("displayDateInfo expects a string, got a type {0} ({1})".format(value.__class__.__name__, value))
        return "n/a"

    # example 2015-11-12T15:01:30.591+0000
    if re.match("\d", value) is not None:

        inputdate = time.strptime(value, "%Y-%m-%dT%H:%M:%S.%f+0000")

        try:
            finisheddate = time.strftime("%H:%M:%S %d/%m/%Y", inputdate).lstrip("0").replace("/0", "/").replace(" 0", " ")
        except:
            return value
        if finisheddate[0] == ':':
            finisheddate = '0'+finisheddate
        return finisheddate
    else:
        return "n/a"