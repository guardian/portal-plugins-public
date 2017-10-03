from django.db import models

class datasource(models.Model):
    name = models.CharField(max_length=255)
    vs_field = models.CharField(max_length=255)
    value_mapping_id = models.CharField(max_length=32768,blank=True,null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"{0}".format(self.name)