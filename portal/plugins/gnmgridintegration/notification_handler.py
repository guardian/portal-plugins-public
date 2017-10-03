from gnmvidispine.vidispine_api import VSApi
import logging

logger = logging.getLogger(__name__)

VIDISPINE_GRID_REF_FIELD = 'gnm_grid_image_refs'


class VSMiniThumb(VSApi):
    def __init__(self,target_frame,framerate,uri,*args,**kwargs):
        self.target_frame = target_frame
        self.framerate = framerate
        self.uri = uri
        super(VSMiniThumb,self).__init__(*args,**kwargs)

    def download(self):
        import re
        print self.host

        partial_url = re.sub('^.*/API','',self.uri)
        content = self.raw_request(path=partial_url,method="GET",accept='image/jpeg')
        return content

    def __unicode__(self):
        return u'Still from frame {0} located at {1}'.format(self.target_frame,self.uri)


class VSMiniThumbCollection(VSApi):
    def setup(self,data):
        import re
        tc_xtract = re.compile('\[TC:(?P<frames>\d+)@(?P<rate>[\d\.]+)\]')

        self.content = []
        for k,v in data.items():
            data = tc_xtract.match(k)
            target_frame = None
            framerate = None
            if data is not None:
                target_frame = int(data.group('frames'))
                framerate = float(data.group('rate'))
            uri = v
            self.content.append(VSMiniThumb(target_frame,framerate,uri,
                                            host=self.host,
                                            port=self.port,
                                            user=self.user,
                                            passwd=self.passwd))

    def each(self):
        for t in self.content:
            yield t


class VidispineResponseWrapper(VSApi):
    def __init__(self, content,*args,**kwargs):
        super(VidispineResponseWrapper,self).__init__(*args,**kwargs)
        self._content = content

    def get(self,key):
        for d in self._content['field']:
            if d['key'] == key:
                return d['value']

    def thumbs(self):
        import json
        tncontent = json.loads(self.get('thumbnails'))
        coll = VSMiniThumbCollection(host=self.host,port=self.port,user=self.user,passwd=self.passwd)
        coll.setup(tncontent)
        return coll

    #example data:
# #{u'field': [{u'key': u'jobId', u'value': u'VX-12'},
#             {u'key': u'closeProxyURI1',
#              u'value': u'file:///srv/media1/theo%20paddling%20pool.mp4\nhttp://127.0.0.1:8080/APInoauth/thumbnail-put/b8d20754-8ae8-44b7-ae5d-bb9baeecd77f'},
#             {u'key': u'currentStepNumber', u'value': u'3'},
#             {u'key': u'type', u'value': u'THUMBNAIL'},
#             {u'key': u'transcodeWallTime', u'value': u'1.43524'},
#             {u'key': u'totalSteps', u'value': u'3'},
#             {u'key': u'createThumbnails', u'value': u'true'},
#             {u'key': u'sequenceNumber', u'value': u'0'},
#             {u'key': u'progress-200-0-0', u'value': u'percent 100.0/100'},
#             {u'key': u'thumbnailTimeCodes', u'value': u'732@PAL'},
#             {u'key': u'transcodeDurations', u'value': u'76800@12800'},
#             {u'key': u'username', u'value': u'admin'},
#             {u'key': u'jobDocument',
#              u'value': u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ComplexJobDocument xmlns="http://xml.gnmvidispine.com/schema/vidispine"><input><id>0</id><uri>file:///srv/media1/theo%20paddling%20pool.mp4</uri><interval><start><samples>311808</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></start><end><samples>388608</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></end></interval></input><connection><input><id>0</id><stream>0</stream></input><videoOutput><edl><timeScale><numerator>1</numerator><denominator>1000</denominator></timeScale><entry start="1024" length="70560" mediaRate="65536"/></edl><setting><key>thumbnailStartOffset</key><value>0@12800</value></setting><generatePosters smallPosters="true"><uri>http://127.0.0.1:8080/API/thumbnail/VX-6/VX-6;version=0</uri><timeCode><samples>732</samples><timeBase><numerator>1</numerator><denominator>25</denominator></timeBase></timeCode></generatePosters></videoOutput></connection></ComplexJobDocument>'},
#             {u'key': u'baseUri', u'value': u'http://127.0.0.1:8080/API/'},
#             {u'key': u'action', u'value': u'STOP'},
#             {u'key': u'transcodeProgress', u'value': u'100.0'},
#             {u'key': u'tags', u'value': u''},
#             {u'key': u'currentStepStatus', u'value': u'FINISHED'},
#             {u'key': u'transcoder', u'value': u'http://localhost:8888/'},
#             {u'key': u'status', u'value': u'FINISHED'},
#             {u'key': u'jobStatusDocument',
#              u'value': u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><JobStatusDocument xmlns="http://xml.gnmvidispine.com/schema/vidispine"><statusUri>http://127.0.0.1:8888/job/VX-12</statusUri><id>VX-12</id><isRunning>false</isRunning><isPaused>false</isPaused><walltime>1.43524</walltime><exitcode>0</exitcode><message>Job ended successfully</message><request><complexRequest><input><id>0</id><uri>file:///srv/media1/theo%20paddling%20pool.mp4</uri><interval><start><samples>311808</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></start><end><samples>388608</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></end></interval></input><connection><input><id>0</id><stream>0</stream></input><videoOutput><edl><timeScale><numerator>1</numerator><denominator>1000</denominator></timeScale><entry start="1024" length="70560" mediaRate="65536"/></edl><setting><key>thumbnailStartOffset</key><value>0@12800</value></setting><generatePosters smallPosters="true"><uri>http://127.0.0.1:8080/APInoauth/thumbnail-put/b8d20754-8ae8-44b7-ae5d-bb9baeecd77f</uri><timeCode><samples>732</samples><timeBase><numerator>1</numerator><denominator>25</denominator></timeBase></timeCode></generatePosters></videoOutput></connection></complexRequest></request><inputProgress><mediaTime><samples>88576</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></mediaTime><duration><samples>76800</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></duration></inputProgress><progress>100.0</progress><estimatedTimeLeft>0.0</estimatedTimeLeft><thumbnail><timeCode><samples>1464</samples><timeBase><numerator>1</numerator><denominator>50</denominator></timeBase></timeCode><uri>http://127.0.0.1:8080/APInoauth/thumbnail-put/b8d20754-8ae8-44b7-ae5d-bb9baeecd77f/1464@50</uri></thumbnail></JobStatusDocument>'},
#             {u'key': u'originalShapeId', u'value': u'VX-11'},
#             {u'key': u'thumbnails',
#              u'value': u'{"[TC:1464@50]":"http://127.0.0.1:8080/API/thumbnail/VX-6/VX-6;version=0/1464@50"}'},
#             {u'key': u'growing', u'value': u'false'},
#             {u'key': u'itemId', u'value': u'VX-6'},
#             {u'key': u'transcodeEstimatedTimeLeft', u'value': u'0.0'},
#             {u'key': u'transcoderId', u'value': u'VX-1'},
#             {u'key': u'transcodeMediaTimes', u'value': u'88576@12800'},
#             {u'key': u'item', u'value': u'VX-6'},
#             {u'key': u'started', u'value': u'2016-02-03T12:45:40.786Z'},
#             {u'key': u'user', u'value': u'admin'},
#             {u'key': u'transcodeDone', u'value': u'true'}]}
# [03/Feb/2016 12:45:43] "POST /portal.plugins.gnmgridintegration/callback/jobnotification HTTP/1.0" 200 4664
# {u'field': [{u'key': u'closeProxyURI2',
#              u'value': u'file:///srv/media1/theo%20paddling%20pool.mp4\nhttp://127.0.0.1:8080/APInoauth/thumbnail-put/d3d3e62c-b0b7-416c-ad02-13ab1d776727'},
#             {u'key': u'jobId', u'value': u'VX-13'},
#             {u'key': u'posterTimeCodes', u'value': u'732@PAL'},
#             {u'key': u'currentStepNumber', u'value': u'3'},
#             {u'key': u'type', u'value': u'THUMBNAIL'},
#             {u'key': u'transcodeWallTime', u'value': u'1.39481'},
#             {u'key': u'totalSteps', u'value': u'3'},
#             {u'key': u'createThumbnails', u'value': u'false'},
#             {u'key': u'sequenceNumber', u'value': u'0'},
#             {u'key': u'progress-200-0-0', u'value': u'percent 100.0/100'},
#             {u'key': u'transcodeDurations', u'value': u'76800@12800'},
#             {u'key': u'username', u'value': u'admin'},
#             {u'key': u'jobDocument',
#              u'value': u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><ComplexJobDocument xmlns="http://xml.gnmvidispine.com/schema/vidispine"><input><id>0</id><uri>file:///srv/media1/theo%20paddling%20pool.mp4</uri><interval><start><samples>311808</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></start><end><samples>388608</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></end></interval></input><connection><input><id>0</id><stream>0</stream></input><videoOutput><edl><timeScale><numerator>1</numerator><denominator>1000</denominator></timeScale><entry start="1024" length="70560" mediaRate="65536"/></edl><setting><key>thumbnailStartOffset</key><value>0@12800</value></setting><generatePosters><uri>http://127.0.0.1:8080/API/poster/VX-6/VX-6;version=0</uri><timeCode><samples>732</samples><timeBase><numerator>1</numerator><denominator>25</denominator></timeBase></timeCode></generatePosters></videoOutput></connection></ComplexJobDocument>'},
#             {u'key': u'baseUri', u'value': u'http://127.0.0.1:8080/API/'},
#             {u'key': u'action', u'value': u'STOP'},
#             {u'key': u'transcodeProgress', u'value': u'100.0'},
#             {u'key': u'tags', u'value': u''},
#             {u'key': u'currentStepStatus', u'value': u'FINISHED'},
#             {u'key': u'transcoder', u'value': u'http://localhost:8888/'},
#             {u'key': u'status', u'value': u'FINISHED'},
#             {u'key': u'jobStatusDocument',
#              u'value': u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><JobStatusDocument xmlns="http://xml.gnmvidispine.com/schema/vidispine"><statusUri>http://127.0.0.1:8888/job/VX-13</statusUri><id>VX-13</id><isRunning>false</isRunning><isPaused>false</isPaused><walltime>1.39481</walltime><exitcode>0</exitcode><message>Job ended successfully</message><request><complexRequest><input><id>0</id><uri>file:///srv/media1/theo%20paddling%20pool.mp4</uri><interval><start><samples>311808</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></start><end><samples>388608</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></end></interval></input><connection><input><id>0</id><stream>0</stream></input><videoOutput><edl><timeScale><numerator>1</numerator><denominator>1000</denominator></timeScale><entry start="1024" length="70560" mediaRate="65536"/></edl><setting><key>thumbnailStartOffset</key><value>0@12800</value></setting><generatePosters><uri>http://127.0.0.1:8080/APInoauth/thumbnail-put/d3d3e62c-b0b7-416c-ad02-13ab1d776727</uri><timeCode><samples>732</samples><timeBase><numerator>1</numerator><denominator>25</denominator></timeBase></timeCode></generatePosters></videoOutput></connection></complexRequest></request><inputProgress><mediaTime><samples>85504</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></mediaTime><duration><samples>76800</samples><timeBase><numerator>1</numerator><denominator>12800</denominator></timeBase></duration></inputProgress><progress>100.0</progress><estimatedTimeLeft>0.0</estimatedTimeLeft><thumbnail><timeCode><samples>1464</samples><timeBase><numerator>1</numerator><denominator>50</denominator></timeBase></timeCode><uri>http://127.0.0.1:8080/APInoauth/thumbnail-put/d3d3e62c-b0b7-416c-ad02-13ab1d776727/1464@50</uri></thumbnail></JobStatusDocument>'},
#             {u'key': u'originalShapeId', u'value': u'VX-11'},
#             {u'key': u'thumbnails',
#              u'value': u'{"[TC:1464@50]":"http://127.0.0.1:8080/API/poster/VX-6/VX-6;version=0/1464@50"}'},
#             {u'key': u'growing', u'value': u'false'},
#             {u'key': u'itemId', u'value': u'VX-6'},
#             {u'key': u'transcodeEstimatedTimeLeft', u'value': u'0.0'},
#             {u'key': u'transcoderId', u'value': u'VX-1'},
#             {u'key': u'transcodeMediaTimes', u'value': u'85504@12800'},
#             {u'key': u'item', u'value': u'VX-6'},
#             {u'key': u'started', u'value': u'2016-02-03T12:45:40.861Z'},
#             {u'key': u'user', u'value': u'admin'},
#             {u'key': u'transcodeDone', u'value': u'true'}]}


def get_and_upload_image(item, thumbpath, identifiers):
    from grid_api import GridLoader
    from django.conf import settings
    import traceback
    loader = GridLoader('pluto_gnmgridintegration', settings.GNM_GRID_API_KEY)

    logger.info("Trying to upload {0} to Grid...".format(thumbpath))

    try:
        with open(thumbpath) as fp:
            gridimage = loader.upload_image(fp) #use default filename
    except GridLoader.HttpError as e:
        logger.error("Unable to upload {0} to Grid: {1}".format(thumbpath, unicode(e)))
        return
    except Exception as e:
        logger.error("{0}: {1}".format(e.__class__, unicode(e)))
        logger.error(traceback.format_exc())
        return
    logger.info("Image {0} uploaded as {1}".format(thumbpath, gridimage.uri))

    current_value = item.get(VIDISPINE_GRID_REF_FIELD, allowArray=True)
    if current_value is None or current_value == "":
        current_value = []
    logger.debug("Current field value is {0}".format(current_value))

    if not isinstance(current_value,list):
        current_value = [current_value]
    current_value.append(gridimage.uri)

    logger.debug("Setting new value {0} to {1}".format(current_value,VIDISPINE_GRID_REF_FIELD))
    item.set_metadata({VIDISPINE_GRID_REF_FIELD: current_value})

    logger.info("Completed get_and_upload_image for {0} from {1}".format(thumbpath,item.name))
    return gridimage


def do_meta_substitution(item, frame_number, type):
    from models import GridMetadataFields
    from traceback import format_exc
    output_meta = {}

    for rec in GridMetadataFields.objects.filter(type=type):
        logger.debug(u"Setting up field {0}".format(unicode(rec)))
        try:
            output_meta[rec.grid_field_name] = rec.real_value(item, frame_number=frame_number)
        except StandardError as e:
            logger.error("{0}: {1}".format(e.__class__,unicode(e)))
            logger.error(format_exc())
            continue

    return output_meta


def vs_field_list():
    from models import GridMetadataFields, GridCapturePreset
    out = []

    for rec in GridMetadataFields.objects.all():
        if rec.vs_field != "" and rec.vs_field is not None:
            out.append(rec.vs_field)

    for rec in GridCapturePreset.objects.all():
        if rec.vs_field != "" and rec.vs_field is not None:
            out.append(rec.vs_field)
    out.append(VIDISPINE_GRID_REF_FIELD)
    return out


def setup_image_metadata(item, grid_image, frame_number=None):
    output_meta = do_meta_substitution(item,frame_number,1)
    grid_image.set_metadata(output_meta)

    output_meta = do_meta_substitution(item, frame_number,2)
    grid_image.set_usage_rights(category=output_meta['category'], source=output_meta['source'])

    grid_image.add_labels(item.name)


def should_trigger(item):
    from models import GridCapturePreset

    for rec in GridCapturePreset.objects.filter(active=True):
        if rec.should_trigger(item):
            return rec.pk
    return False


def get_new_thumbnail(notification_data):
    from django.conf import settings
    import os.path
    import traceback
    import time
    from gnmvidispine.vs_item import VSItem
    from grid_api import GridImage
    tempdir = "/tmp"

    retry_delay = 5
    if hasattr(settings,'GRID_RETRY_DELAY'):
        retry_delay = int(settings.GRID_RETRY_DELAY)
    max_retries=10
    if hasattr(settings,'GRID_MAX_RETRIES'):
        max_retries = int(settings.GRID_MAX_RETRIES)

    resp = VidispineResponseWrapper(notification_data,url=settings.VIDISPINE_URL,user=settings.VIDISPINE_USERNAME,
                                    passwd=settings.VIDISPINE_PASSWORD)
    logger.info("Notified of new thumbnail for {0}".format(resp.get('itemId')))
    if resp.get('createThumbnails') != 'false':
        #if we don't filter this out, we get crappy small thumbnails as well, but we only want nice big poster frames
        logger.info("Got createThumbnails={0} (expecting false, i.e. Poster frame was created). Not continuing.".format(resp.get('createThumbnails')))
        return

    total = 0
    item = VSItem(url=settings.VIDISPINE_URL,port=settings.VIDISPINE_PORT,
                  user=settings.VIDISPINE_USERNAME,passwd=settings.VIDISPINE_PASSWORD)
    logger.info("Looking up associated item {0}".format(resp.get('itemId')))
    item.populate(resp.get('itemId'),specificFields=vs_field_list())

    n=should_trigger(item)
    if not n:
        logger.info("Not triggering on item {0} because it does not match enabling profiles. Go to Grid Integration in the Portal admin panel if you think this is incorrect.".format(item.name))
        return
    logger.info("Item {0} matched profile id {1} so continuing".format(item.name,n))

    for t in resp.thumbs().each():
        filename = "{item}_{frm}.jpg".format(item=resp.get('itemId'),frm=str(t.target_frame))
        outpath = os.path.join(tempdir,filename)
        logger.debug("Outputting to {0}".format(outpath))
        with open(outpath,'w') as f:
            f.write(t.download())
        img = get_and_upload_image(item, outpath, [])
        setup_image_metadata(item, img, frame_number = t.target_frame)
        retries = 0

        while True:
            try:
                #if it's a 'recognised' 16x9 video size then supply a crop as a convenience
                if img.width ==1920 and img.height==1080:
                    img.make_crop(0,0,1920,1080)
                elif img.width==1280 and img.height==720:
                    img.make_crop(0,0,1280,720)
                break
            except GridImage.CropsNotAvailable as e:
                logger.warning(e)
                retries+=1
                if retries>= max_retries:
                    logger.error("Could not crop after {0} attempts, giving up".format(retries))
                    break
                time.sleep(retry_delay)

            except StandardError as e:
                logger.error(unicode(e))
                logger.error(traceback.format_exc())
                break
        total +=1
        try:
            os.unlink(outpath)
        except StandardError as e:
            logger.warning(unicode(e))

    logger.info("Handler completed for {0}, processed {1} thumbs".format(resp.get('itemId'), total))