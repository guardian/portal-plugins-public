# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'StorageData.incident_key'
        db.alter_column('gnmpagerduty_storagedata', 'incident_key', self.gf('django.db.models.fields.CharField')(default='', max_length=64))

    def backwards(self, orm):

        # Changing field 'StorageData.incident_key'
        db.alter_column('gnmpagerduty_storagedata', 'incident_key', self.gf('django.db.models.fields.CharField')(max_length=64, null=True))

    models = {
        'gnmpagerduty.storagedata': {
            'Meta': {'object_name': 'StorageData'},
            'current_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'maximum_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'storage_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'trigger_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gnmpagerduty']

