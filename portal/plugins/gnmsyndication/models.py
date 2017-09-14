from django.db import models

class platform(models.Model):
    name = models.CharField(max_length=512,unique=True,null=False)
    intention_label = models.CharField(max_length=512,unique=True,blank=True,null=True) #as it appears in gnm_master_generic_intendeduploadplatforms
    uploadstatus_field = models.CharField(max_length=512,blank=False)
    publicationstatus_field = models.CharField(max_length=512,blank=False)
    publicationtime_field = models.CharField(max_length=512,blank=False)
    enabled_icon_url = models.CharField(max_length=512,blank=True,null=True)
    disable_icon_url = models.CharField(max_length=512,blank=True,null=True)
    display_icon_url = models.CharField(max_length=512,blank=True,null=True)

    def __unicode__(self):
        return u'{0} {1}'.format(self.name,self.uploadstatus_field)

    class Meta:
        ordering = ['name']
