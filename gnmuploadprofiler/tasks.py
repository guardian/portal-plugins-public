from celery import shared_task
import logging

logger = logging.getLogger(__name__)


def changesets_for_fieldname(fieldname,changeset_list):
    rtn = []
    for cs in changeset_list:
        if cs.fields is None: continue
        #print "Checking for {0} in {1}".format(fieldname,cs.fields)
        if fieldname in cs.fields:
            rtn.append(cs)
    return rtn


def last_change_from_set(changeset_list):
    from datetime import datetime
    import pytz
    rtn = None
    last_timestamp = datetime(1970,1,1,tzinfo=pytz.timezone('UTC'))

    for cs in changeset_list:
        for change in cs.changes():
            if change.timestamp > last_timestamp:
                rtn = change
                last_timestamp = change.timestamp

    return rtn


def change_for_value(value,changeset_list):
    rtn = None
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


@shared_task
def profile_item(itemname):
    """
    Calculate the times for the various waypoints to publishing this item.  Assumes that the item has actually been published.
    :param itemname: Vidispine ID for the item to profile
    :return: Saved database model record
    """
    from gnmvidispine.vs_item import VSItem
    from django.conf import settings
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
    profile_record.item_duration = item.get('durationSeconds')

    #step one - created time
    profile_record.created_time = dateutil.parser.parse(item.get('created'))
    print("Created time is {0}".format(profile_record.created_time))

    print("portal_ingested is {0}".format(item.get('portal_ingested')))

    subset = changesets_for_fieldname('shapeTag',changeset_list)
    lastchange = last_change_from_set(subset)
    print("last change of shapeTag is {0}".format(unicode(lastchange)))

    interval = lastchange.timestamp - profile_record.created_time
    print("Time interval is {0}".format(interval))
    profile_record.proxy_completed_interval = timedelta_to_float(interval)

    subset = changesets_for_fieldname('gnm_master_website_uploadstatus',changeset_list)
    #print "got subset {0}".format(subset)
    readychange = change_for_value('Ready to Upload',subset)
    print("trigger change was {0}".format(unicode(readychange)))
    profile_record.upload_trigger_interval=timedelta_to_float(readychange.timestamp - profile_record.created_time)

    #page_created_interval
    subset = changesets_for_fieldname('gnm_master_website_edit_url',changeset_list)
    lastchange = last_change_from_set(subset)
    print("last change of gnm_master_website_edit_url is {0}".format(lastchange))
    profile_record.page_created_interval=timedelta_to_float(lastchange.timestamp - profile_record.created_time)

    #last transcode
    subset = changesets_for_fieldname('gnm_master_website_uploadlog',changeset_list)
    lastchange = last_change_from_set(subset)
    print("last change of gnm_master_website_uploadlog is {0}".format(lastchange))
    profile_record.final_transcode_completed_interval = timedelta_to_float(lastchange.timestamp - profile_record.created_time)

    #page launch guess
    launchguess = dateutil.parser.parse(item.get('gnm_master_publication_time'))
    profile_record.page_launch_guess_interval = timedelta_to_float(launchguess - profile_record.created_time)

    #last timestamp, for sorting.
    profile_record.completed_time = launchguess

    pprint(profile_record.__dict__)
    profile_record.save()
    return profile_record