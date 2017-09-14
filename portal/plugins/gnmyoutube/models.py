from django.db import models


class settings(models.Model):
    key = models.CharField(max_length=255,db_index=True,unique=True)
    value = models.CharField(max_length=32768)

    def __unicode__(self):
        return u'{0} => {1}'.format(self.key,self.value)