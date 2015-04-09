from django.forms import Form,ChoiceField,CharField,TextInput,CheckboxSelectMultiple,Textarea,MultipleChoiceField,Select
import urllib

class LogSearchForm(Form):
    class FormNotValid(StandardError):
        pass

    #matrix parameters for call
    type = MultipleChoiceField(choices=(('All','all'),
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
    sort = ChoiceField(choices=(('None',None),

                            ),widget=Select(attrs={'style': 'width: 98%'})
                    )
    #Query parameters for call
    jobmetadata = CharField(max_length=32768,widget=Textarea)

    #my own params which will be put into the above
    fileNameContains = CharField(max_length=512,widget=TextInput(attrs={'style': 'width: 98%'}))

    def vidispine_query_url(self,base):
        if not self.is_valid():
            raise self.FormNotValid()

        d = self.cleaned_data

        matrixparams = ";state=" + ",".join(map(lambda x: urllib.quote_plus(x,safe=""),d['state']))
        matrixparams += ";type=" + ",".join(map(lambda x: urllib.quote_plus(x,safe=""),d['type']))
        matrixparams += ";sort=" + urllib.quote_plus(d['sort'],safe="")
        queryparams = "?jobmetadata=" + urllib.quote_plus(d['jobmetadata'],safe="")

        return base + matrixparams + queryparams