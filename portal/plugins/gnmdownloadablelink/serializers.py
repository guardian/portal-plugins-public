from rest_framework.serializers import ModelSerializer

from models import DownloadableLink


class DownloadableLinkSerializer(ModelSerializer):
    def __init__(self,*args,**kwargs):
        super(DownloadableLinkSerializer,self).__init__(*args,**kwargs)
        if 'defaults' in kwargs:
            self.defaults = kwargs['defaults']

    class Meta:
        model = DownloadableLink
        fields = ('public_url', 'status', 'created', 'created_by',
                  'expiry', 'item_id', 'shapetag', 'transcode_job')

    # def validate_created_by(self, attrs):
    #     if self.data['created_by'] is None and 'request' in self.context:
    #         self.data['created_by'] = self.context['request'].user
    #
    #def perform_validation(self, attrs):
    #     if 'request' in self.context:
    #         request = self.context['request']
    #         print "Got request reference. User is {0}".format(request.user)
    #         print self.data
    #         print self.data['created_by']
    #         if self.data['created_by'] == "" or self.data['created_by'] is None:
    #             print "filling in created_by"
    #             self.data['created_by'] = request.user
    #         print self.data
    #     else:
    #         print "No request in serializer context"
    #     return super(DownloadableLinkSerializer, self).perform_validation(attrs)