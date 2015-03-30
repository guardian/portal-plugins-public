from django.db import models

class datasource(models.Model):
    name = models.CharField(max_length=255)
    vs_field = models.CharField(max_length=255)
    value_mapping_id = models.CharField(max_length=32768)

    class Meta:
        ordering = ['name']