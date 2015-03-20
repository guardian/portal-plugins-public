#https://docs.djangoproject.com/en/1.7/howto/custom-template-tags/

from django import template
from django.utils.safestring import mark_safe
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