from celery import shared_task
from contentapi import lookup_by_octid
import logging
import re

logger = logging.getLogger(__name__)


def changesets_for_fieldname(fieldname,changeset_list):
    rtn = []
    for cs in changeset_list:
        if cs.fields is None: continue
        #print "Checking for {0} in {1}".format(fieldname,cs.fields)
        if fieldname in cs.fields:
            rtn.append(cs)
    return rtn


def _is_change_matching(change,fieldname=None,value=None):
    if fieldname is not None:
        if hasattr(fieldname,"search"): #it's a regex-like object
            result = fieldname.search(change.fieldname)
            if result is None:
                return False
        elif change.fieldname != str(fieldname): #it's a string-like object
            return False
    if value is not None:
        if hasattr(value,"search"): #it's a regex-like object
            result = value.search(change.value)
            print "regex search for {0} against {1} gave {2}".format(value,change.value,result)
            if result is None:
                return False
        elif isinstance(change.value, list): #it's a list
            if value not in change.value:
                return False
        else:
            if change.value != str(fieldname): #it's a string-like object
                return False
    # if value is not None and not isinstance(change.value, list) and value != change.value:
    #     print "continuing as '{0}' ({3}) is not equal to '{1}' ({4}) for {2}".format(value, change.value,
    #                                                                                  change.fieldname,
    #                                                                                  value.__class__.__name__,
    #                                                                                  change.value.__class__.__name__)
    #     return False
    return True


def first_change_from_set(changeset_list,fieldname=None,value=None):
    from datetime import datetime
    import pytz
    rtn = None
    first_timestamp = datetime.now(tz=pytz.UTC)

    for cs in changeset_list:
        for change in cs.changes():
            if not _is_change_matching(change,fieldname,value): #if fieldname and value are both None, this check is effectively bypassed
                continue
            if change.timestamp < first_timestamp:
                rtn = change
                first_timestamp = change.timestamp

    return rtn


def last_change_from_set(changeset_list,fieldname=None,value=None):
    from datetime import datetime
    import pytz
    rtn = None
    last_timestamp = datetime(1970,1,1,tzinfo=pytz.timezone('UTC'))

    for cs in changeset_list:
        for change in cs.changes():
            if not _is_change_matching(change,fieldname,value):
                continue

            if change.timestamp > last_timestamp:
                rtn = change
                last_timestamp = change.timestamp

    return rtn


def change_for_value(value,changeset_list):
    rtn = None
    changeset_list.sort(key=lambda x: x.name)
    for cs in changeset_list:
        for change in cs.changes():
            if isinstance(change.value,list):
                #print "checking for {0} in {1}".format(value,change.value)
                if value in change.value:
                    rtn = change
                    break
            else:
                #print "checking for {0} against {1}".format(value,change.value)
                if change.value == value:
                    rtn = change
                    break
        if rtn is not None:
            break
    return rtn


def timedelta_to_float(td):
    return (float(td.days)*24*3600) + float(td.seconds) + (float(td.microseconds)/1000000)


class UploadLog(object):
    run_text_delimiter = "Acquiring media..." #this text shows the start of a new upload run

    def __init__(self):
        self.content = []
        self.upload_runs = []

    def parse_upload_log(self,logstring, assumed_date=None):
        from datetime import datetime
        import pytz
        lines = logstring.split("\n")

        if not isinstance(assumed_date,datetime): raise TypeError

        matcher = re.compile(r'^(\d{2}):(\d{2}):(\d{2})\s*(.*)$')
        for l in lines:
            parts = matcher.match(l)
            if parts:
                hrs = int(parts.group(1))
                mins = int(parts.group(2))
                sec = int(parts.group(3))
                text = parts.group(4)

                #timestamp = hrs*3600 + mins*60 + sec
                timestamp = assumed_date.replace(hour=hrs,minute=mins,second=sec,microsecond=0)
                self.content.append({'timestamp': timestamp, 'text': text})
                if text==self.run_text_delimiter:
                    self.upload_runs.append(len(self.content))

    @property
    def upload_run_count(self):
        return len(self.upload_runs)

    def upload_run(self,run_number):
        if not isinstance(run_number,int):
            raise TypeError
        if run_number>self.upload_run_count:
            raise ValueError("There are only {0} runs to choose from".format(self.upload_run_count))
        if run_number<0:
            raise ValueError("Run number must be greater than zero")

        end_index=self.upload_runs[run_number]
        if run_number>0:
            start_index=self.upload_runs[run_number-1]
        else:
            start_index=0

        return self.content[start_index:end_index]

@shared_task
def profile_item(itemname):
    """
    Calculate the times for the various waypoints to publishing this item.  Assumes that the item has actually been published.
    :param itemname: Vidispine ID for the item to profile
    :return: Saved database model record
    """
    from gnmvidispine.vs_item import VSItem
    from django.conf import settings
    from datetime import timedelta
    import dateutil.parser
    from models import OutputTimings
    from pprint import pprint

    print("Doing output time profile for item {0}".format(itemname))
    item = VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                  user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    item.populate(itemname)

    changeset_list = item.metadata_changeset_list()

    try:
        profile_record = OutputTimings.objects.get(item_id=itemname)
        logger.warning(u"Item {0} ({1}) has already been profiled!".format(itemname,item.get('title')))
        print(u"Item {0} ({1}) has already been profiled!".format(itemname,item.get('title')))
    except OutputTimings.DoesNotExist:
        profile_record = OutputTimings()

    profile_record.item_id = item.name
    profile_record.commission = item.get('gnm_commission_title')
    profile_record.project = item.get('gnm_project_headline')
    profile_record.item_duration = item.get('durationSeconds')

    #step one - created time
    profile_record.created_time = dateutil.parser.parse(item.get('created'))
    print("Created time is {0}".format(profile_record.created_time))

    print("portal_ingested is {0}".format(item.get('portal_ingested')))

    #when was the media last added?
    current_version = item.get('portal_essence_version')
    #for the time being, ignoring updates; therefore we're looking for the creation of version 1.
    subset = changesets_for_fieldname('portal_essence_version',changeset_list)
    lastchange = first_change_from_set(subset,fieldname='portal_essence_version')#,value=str(1))
    print("change of portal_essence_version is {0}".format(unicode(lastchange)))
    if lastchange is not None:
        profile_record.version_created_time = lastchange.timestamp
        profile_record.media_version = int(current_version) #int(lastchange.value)

    subset = changesets_for_fieldname('shapeTag',changeset_list)
    #lastchange = last_change_from_set(subset)
    #print("last change of shapeTag is {0}".format(unicode(lastchange)))
    lastchange = change_for_value('lowres',subset)
    print("change of shapeTag to have lowres is {0}".format(unicode(lastchange)))
    interval = lastchange.timestamp - profile_record.version_created_time
    print("Time interval is {0}".format(interval))
    profile_record.proxy_completed_interval = timedelta_to_float(interval)

    subset = changesets_for_fieldname('gnm_master_website_uploadstatus',changeset_list)
    #print "got subset {0}".format(subset)
    readychange = change_for_value('Ready to Upload',subset)
    print("trigger change was {0}".format(unicode(readychange)))
    profile_record.upload_trigger_interval=timedelta_to_float(readychange.timestamp - profile_record.version_created_time)
    if profile_record.upload_trigger_interval<0:
        profile_record.upload_trigger_interval = timedelta_to_float(readychange.timestamp - profile_record.created_time)
    #page_created_interval
    subset = changesets_for_fieldname('gnm_master_website_edit_url',changeset_list)
    #lastchange = last_change_from_set(subset)
    lastchange = first_change_from_set(subset,value=re.compile('.+'))
    print("first non-empty change of gnm_master_website_edit_url is {0}".format(lastchange))
    profile_record.page_created_interval=timedelta_to_float(lastchange.timestamp - profile_record.version_created_time)

    #last transcode
    subset = changesets_for_fieldname('gnm_master_website_uploadlog',changeset_list)
    firstchange = first_change_from_set(subset)
    log = UploadLog()
    log.parse_upload_log(item.get('gnm_master_website_uploadlog'),assumed_date=firstchange.timestamp)
    # print("There were {0} upload runs total:".format(log.upload_run_count))
    # for n in range(0,log.upload_run_count):
    #     pprint(log.upload_run(n))
    first_run=log.upload_run(log.upload_run_count-1)
    while True:
        print("last transcode of the first run was at {0} ({1})".format(first_run[0]['timestamp'], first_run[0]['text']))
        profile_record.final_transcode_completed_interval = timedelta_to_float(first_run[0]['timestamp'] - profile_record.version_created_time)
        if profile_record.final_transcode_completed_interval >0:
            break
        first_run[0]['timestamp']+=timedelta(days=1)

    #lastchange = last_change_from_set(subset)
    #print("last change of gnm_master_website_uploadlog is {0}".format(lastchange))
    #profile_record.final_transcode_completed_interval = timedelta_to_float(lastchange.timestamp - profile_record.version_created_time)

    #page launch guess
    launchguess = dateutil.parser.parse(item.get('gnm_master_publication_time'))
    profile_record.page_launch_guess_interval = timedelta_to_float(launchguess - profile_record.version_created_time)

    #page launch from capi
    capi_data = lookup_by_octid(item.get('gnm_master_generic_titleid'))
    profile_record.page_launch_capi_interval = timedelta_to_float(capi_data['webPublicationDate'] - profile_record.version_created_time)
    profile_record.page_launch_pluto_lag = timedelta_to_float(launchguess - capi_data['webPublicationDate'])

    #last timestamp, for sorting.
    #profile_record.completed_time = launchguess
    profile_record.completed_time = capi_data['webPublicationDate']

    pprint(profile_record.__dict__)
    profile_record.save()
    return profile_record