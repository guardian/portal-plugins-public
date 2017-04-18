# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'StorageData', fields ['storage_id']
        db.create_unique('gnmpagerduty_storagedata', ['storage_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'StorageData', fields ['storage_id']
        db.delete_unique('gnmpagerduty_storagedata', ['storage_id'])


    models = {
        'gnmpagerduty.storagedata': {
            'Meta': {'object_name': 'StorageData'},
            'current_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'storage_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'trigger_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gnmpagerduty']