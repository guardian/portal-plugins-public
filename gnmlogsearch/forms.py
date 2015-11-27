from django.forms import Form,ChoiceField,CharField,DateField,TimeField,TextInput,CheckboxSelectMultiple,RadioSelect,Textarea,MultipleChoiceField,Select,ValidationError
import urllib

class LogSearchForm(Form):
    class FormNotValid(StandardError):
        pass
    import logging

    #matrix parameters for call
    type = MultipleChoiceField(choices=(('all','All'),
                                ('DELETE_LIBRARY','DELETE_LIBRARY'),
                                ('UPDATE_LIBRARY_ITEM_METADATA','UPDATE_LIBRARY_ITEM_METADATA'),
                                ('NONE','NONE'),
                                ('IMPORT','IMPORT'),
                                ('TRANSCODE','TRANSCODE'),
                                ('RAW_TRANSCODE','RAW_TRANSCODE'),
                                ('CONFORM','CONFORM'),
                                ('TRANSCODE_RANGE','TRANSCODE_RANGE'),
                                ('PLACEHOLDER_IMPORT','PLACEHOLDER_IMPORT'),
                                ('RAW_IMPORT','RAW_IMPORT'),
                                ('THUMBNAIL','THUMBNAIL'),
                                ('AUTO_IMPORT','AUTO_IMPORT'),
                                ('EXPORT','EXPORT'),
                                ('COPY_FILE','COPY_FILE'),
                                ('DELETE_FILE','DELETE_FILE'),
                                ('MOVE_FILE','MOVE_FILE'),
                                ('ESSENCE_VERSION','ESSENCE_VERSION'),
                                ('FCS_RESTORE','FCS_RESTORE'),
                                ('TIMELINE','TIMELINE'),
                                ('SHAPE_IMPORT','SHAPE_IMPORT'),
                                ('LIST_ITEMS','LIST_ITEMS'),
                                ('ANALYZE','ANALYZE'),
                                ('SHAPE_UPDATE','SHAPE_UPDATE'),
                                ('ARCHIVE','ARCHIVE'),
                                ('RESTORE','RESTORE'),
                                ('SIDECAR_IMPORT','SIDECAR_IMPORT'),
                                ('TEST_TRANSFER','TEST_TRANSFER'),
                            ),widget=CheckboxSelectMultiple()
                       )
    state = MultipleChoiceField(choices=(('all','All'),
                                 ('NONE','None'),
                                 ('READY','Ready'),
                                 ('STARTED','Started'),
                                 ('STARTED_ASYNCHRONOUS','Started Asynchronous'),
                                 ('STARTED_PARALLEL','Started in background'),
                                 ('STARTED_PARALLEL_ASYNCHRONOUS','Started in background, asynchronous'),
                                 ('STARTED_SUBTASKS','Started and doing in multiple subtasks'),
                                 ('FINISHED','Completed'),
                                 ('FAILED_RETRY','Retrying'),
                                 ('FAILED_FATAL','Failed'),
                                 ('FAILED_TOTAL','Failed'),
                                 ('WAITING','Waiting'), #see /job/{job-id}/problem
                                 ('DISAPPEARED','Disappeared, lost worker')
                            ),widget=CheckboxSelectMultiple()
                        )
    sort = ChoiceField(choices=(('startTime','Start Time'),
                                ('priority','Priority'),
                                ('jobId','Job ID'),
                                ('type','Type'),
                                ('state','State'),
                                ('user','User'),
                            ),widget=Select(attrs={'style': 'width: 98%'})
                    )
    sortOrder = ChoiceField(choices=(('desc','Descending'),
                                     ('asc','Ascending'),
                            ), widget=RadioSelect(),
                    )
    fromDate = DateField(label="Starting from",widget=TextInput(attrs={'style': 'width: 60%'}))
    fromTime = TimeField(label="Starting from",widget=TextInput(attrs={'style': 'width: 60%'}))

    toDate = DateField(label="Ending at",widget=TextInput(attrs={'style': 'width: 60%'}))
    toTime = TimeField(label="Ending at",widget=TextInput(attrs={'style': 'width: 60%'}))

    #Query parameters for call
    jobmetadata = CharField(max_length=32768,widget=Textarea,required=False)

    #my own params which will be put into the above
    fileNameContains = CharField(max_length=512,widget=TextInput(attrs={'style': 'width: 98%; visibility: hidden'}),required=False)

    columns = MultipleChoiceField(choices=(('jobId','jobId'),
                                ('status','status'),
                                ('type','type'),
                                ('started','started'),
                                ('priority','priority'),
                                ('itemid','itemid'),
                                ('systemJobModule','systemJobModule'),
                                ('systemJobInfo','systemJobInfo'),
                                ('destinationStorageId','destinationStorageId'),
                                ('bestEffortFilename','bestEffortFilename'),
                                ('fileId','fileId'),
                                ('replicatedFileIds','replicatedFileIds'),
                                ('fileDeleted','fileDeleted'),
                                ('fileStateOnFailure','fileStateOnFailure'),
                                ('filePathMap','filePathMap'),
                                ('replicatedFileInfo','replicatedFileInfo'),
                                ('checkReplicatedFiles','checkReplicatedFiles'),
                            ),widget=CheckboxSelectMultiple()
                       )

    def vidispine_query_url(self,base,page):
        from datetime import datetime
        import time
        import calendar

        if not self.is_valid():
            raise self.FormNotValid()

        #logger=self.logging.getLogger("LogSearchForm::vidispine_query_url")
        d = self.cleaned_data

        if page == 1:
            pagesetting = 0
        else:
            pagesetting = page * 100 - 100

        pagesettingready = str(pagesetting)

        matrixparams = ""
        if not 'all' in d['state']:
            matrixparams += ";state=" + ",".join(map(lambda x: urllib.quote_plus(x,safe=""),d['state']))
        if not 'all' in d['type']:
            matrixparams += ";type=" + ",".join(map(lambda x: urllib.quote_plus(x,safe=""),d['type']))
        matrixparams += ";number=100;first=" + pagesettingready + ";sort={0}%20{1}".format(urllib.quote_plus(d['sort'],safe=""),d['sortOrder'])
        queryparams = "?metadata=true"

        if d['fileNameContains']:
            queryparams += "&jobmetadata=" + urllib.quote_plus("bestEffortFilename=*{0}*".format(d['fileNameContains']),safe="")

        if d['jobmetadata']:
            queryparams += "&jobmetadata=" + urllib.quote_plus(d['jobmetadata'],safe="")

        fromTime = datetime.combine(d['fromDate'],d['fromTime'])
        toTime = datetime.combine(d['toDate'],d['toTime'])
        queryparams += "&starttime-from=" + urllib.quote_plus(fromTime.strftime("%Y-%m-%dT%H:%M:%S.%f"),safe="")
        queryparams += "&starttime-to=" + urllib.quote_plus(toTime.strftime("%Y-%m-%dT%H:%M:%S.%f"),safe="")

        print "debug: vidispine_query_url is {0}".format(base + matrixparams + queryparams)
        return base + matrixparams + queryparams