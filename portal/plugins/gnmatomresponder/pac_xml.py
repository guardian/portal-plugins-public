from s3_mixin import S3Mixin
from vs_mixin import VSMixin
import urlparse
import logging

logger = logging.getLogger(__name__)


class PacXmlProcessor(S3Mixin, VSMixin):
    default_expiry_time = 360

    @staticmethod
    def get_admin_user():
        from django.contrib.auth.models import User
        try:
            return User.objects.get(username="admin")
        except User.DoesNotExist:
            admins = User.objects.filter(is_superuser=True)
            if admins.count()>0:
                return admins[0]
            else:
                raise RuntimeError("No admin users could be found in the system, surely this is not right?")

    def link_to_item(self, pac_xml_record, vsitem):
        """
        Performs the connection of data to an item.
        :param pac_xml_record: Instance of models.PacFormXml describing to data to link
        :param vsitem: populated gnmvidispine.vs_item object
        :return:
        """
        from portal.plugins.gnm_masters.edl_import import update_edl_data

        parsed = urlparse.urlparse(pac_xml_record.pacdata_url)
        if parsed.scheme != "s3":
            raise RuntimeError("Only PAC data download from S3 is supported at present")

        pac_xml_record.status = "DOWNLOADING"
        pac_xml_record.save()
        
        logger.info("{n}: Downloading PAC data from {0}".format(pac_xml_record.pacdata_url,n=vsitem.name))
        if parsed.path[0]=='/': #s3 does not like leading /
            s3path = parsed.path[1:]
        else:
            s3path = parsed.path

        filename = self.download_to_local_location(bucket=parsed.hostname, key=s3path)
        logger.info("{n}: Download completed".format(n=vsitem.name))

        with open(filename,"r") as f:
            logger.info("{n}: Linking EDL data from {0}".format(filename,n=vsitem.name))
            pac_xml_record.status = "INPROGRESS"
            pac_xml_record.save()
            task_id = update_edl_data(f, vsitem.name, self.get_admin_user())
        logger.info("{n}: Commenced EDL ingest in celery task {0}".format(task_id, n=vsitem.name))
