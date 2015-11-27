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
        return mark_safe(u"<img style=\"height: 16px\" src=\"{0}\">{1}".format(icon,value))
    else:
        return value

@register.filter("filepath_formatter")
def filePathFormatter(value):
    import uuid

    offset = 0
    n = 0
    #stringhash = hashlib.md5(value).hexdigest()
    stringhash = str(uuid.uuid4())
    parts = []

    for word in value.split('/'):
        if len(word)<1: continue

        parts.append(u"<span class=\"filepath\" style=\"margin-left: {offset}px\"><img style=\"height: 16px\" src=\"{icon}\">{text}</span><br>".format(
            offset=offset,
            icon="/sitemedia/img/logsearch/folder.png",
            text=word
        ))
        offset+=0

    rtn = u"<a onClick=\"toggleFilepathDisplay('{id}');\" style=\"cursor: pointer\">show path...</a><br><div id=\"{id}\" style=\"display: none\">".format(
        id=stringhash
    ) + "".join(parts[:len(parts)-1]) + u"</div>" + u"<span class=\"filepath\" style=\"margin-left: {offset}px\"><img style=\"height: 16px\" src=\"{icon}\">{text}</span><br>".format(
            offset=offset,
            icon="/sitemedia/img/logsearch/file.png",
            text=value.split('/')[-1]
        )
    return mark_safe(rtn)

@register.filter("displaydateinfo")
def displayDateInfo(value):

    import time
    import re
    import calendar

    if re.match("\d", value) is not None:
        # example 2015-11-12T15:01:30.591+0000
        inputdate2 = time.strptime(value, "%Y-%m-%dT%H:%M:%S.%f" + value[23] + value[24] + value[25] + value[26] + value[27])
        inputdate3 = calendar.timegm(inputdate2)
        tzvalue = value[24] + value[25]
        tzvalue2 = int(tzvalue)

        if value[23] == "+":
            inputdate4 = inputdate3 + (tzvalue2 * 60)
        else:
            inputdate4 = inputdate3 - (tzvalue2 * 60)

        inputdate = time.localtime(inputdate4)

        try:
            finisheddate = time.strftime("%H:%M:%S %d/%m/%Y %Z", inputdate).lstrip("0").replace("/0", "/").replace(" 0", " ")
        except:
            return value
        if finisheddate[0] == ':':
            finisheddate = '0'+finisheddate
        return finisheddate
    else:
        return "n/a"

@register.filter("filepathmap")
def filePathMap(value):
    import re

    #value2 = value.replace(",", "</li><li>")

    value2 = re.sub(r"\,(?!\s)", "</li><li>", value)

    return mark_safe("<ul><li>" + value2 + "</li><ul>")