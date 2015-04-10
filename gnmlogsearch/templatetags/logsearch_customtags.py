#https://docs.djangoproject.com/en/1.7/howto/custom-template-tags/

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

 # ('NONE','None'),
 # ('READY','Ready'),
 # ('STARTED','Started'),
 # ('STARTED_ASYNCHRONOUS','Started Asynchronous'),
 # ('STARTED_PARALLEL','Started in background'),
 # ('STARTED_PARALLEL_ASYNCHRONOUS','Started in background, asynchronous'),
 # ('STARTED_SUBTASKS','Started and doing in multiple subtasks'),
 # ('FINISHED','Completed'),
 # ('FAILED_RETRY','Retrying'),
 # ('FAILED_FATAL','Failed'),
 # ('FAILED_TOTAL','Failed'),
 # ('WAITING','Waiting'), #see /job/{job-id}/problem
 # ('DISAPPEARED','Disappeared, lost worker')

@register.filter("jobstatus_formatter")
def jobStatusFormatter(value):
    import re
    classname = value.lower()

    icon_path = '/sitemedia/img/gnm/'
    icon = ""
    if value == 'FINISHED':
        icon = icon_path + 'severity_0.png'
    elif re.match(r'^STARTED',value):
        icon = icon_path + 'loading.gif'
    elif value == 'WAITING':
        icon = icon_path + 'severity_2.png'
    elif value == 'READY':
        icon = icon_path + 'ready_to_publish.png'
    elif re.match(r'^FAILED',value):
        icon = icon_path + 'severity_3.png'

    return mark_safe(u"<span class=\"{0}\"><img src=\"{1}\">{2}</span>".format(classname,icon,value))

# ('DELETE_LIBRARY','DELETE_LIBRARY'),
# ('UPDATE_LIBRARY_ITEM_METADATA','UPDATE_LIBRARY_ITEM_METADATA'),
# ('NONE','NONE'),
# ('IMPORT','IMPORT'),
# ('TRANSCODE','TRANSCODE'),
# ('RAW_TRANSCODE','RAW_TRANSCODE'),
# ('CONFORM','CONFORM'),
# ('TRANSCODE_RANGE','TRANSCODE_RANGE'),
# ('PLACEHOLDER_IMPORT','PLACEHOLDER_IMPORT'),
# ('RAW_IMPORT','RAW_IMPORT'),
# ('THUMBNAIL','THUMBNAIL'),
# ('AUTO_IMPORT','AUTO_IMPORT'),
# ('EXPORT','EXPORT'),
# ('COPY_FILE','COPY_FILE'),
# ('DELETE_FILE','DELETE_FILE'),
# ('MOVE_FILE','MOVE_FILE'),
# ('ESSENCE_VERSION','ESSENCE_VERSION'),
# ('FCS_RESTORE','FCS_RESTORE'),
# ('TIMELINE','TIMELINE'),
# ('SHAPE_IMPORT','SHAPE_IMPORT'),
# ('LIST_ITEMS','LIST_ITEMS'),
# ('ANALYZE','ANALYZE'),
# ('SHAPE_UPDATE','SHAPE_UPDATE'),
# ('ARCHIVE','ARCHIVE'),
# ('RESTORE','RESTORE'),
# ('SIDECAR_IMPORT','SIDECAR_IMPORT'),
# ('TEST_TRANSFER','TEST_TRANSFER'),
@register.filter("jobtype_formatter")
def jobTypeFormatter(value):
    import re

    iconpath = '/sitemedia/img/logsearch/'
    icon = ""

    if re.match(r'^DELETE',value):
        icon = iconpath + "delete.png"
    elif re.match(r'^COPY',value):
        icon = iconpath + "copy.png"
    elif re.match(r'^MOVE',value):
        icon = iconpath + "move.png"
    elif re.search(r'TRANSCODE',value):
        icon = iconpath + "transcode.png"
    elif re.search(r'IMPORT',value):
        icon = iconpath + "import.png"
    elif re.search(r'RESTORE',value):
        icon = iconpath + "restore.png"
    elif re.search(r'ARCHIVE',value):
        icon = iconpath + "archive.png"
    elif re.search(r'ANALYZE',value):
        icon = iconpath + "analyze.png"
    elif re.match(r'TRANSFER',value):
        icon = iconpath + "transfer.png"

    if icon != "":
        return mark_safe(u"<img src=\"{0}\">{1}".format(icon,value))
    else:
        return value