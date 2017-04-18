# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'StorageData.current_size'
        db.delete_column('gnmpagerduty_storagedata', 'current_size')

        # Deleting field 'StorageData.incident_key'
        db.delete_column('gnmpagerduty_storagedata', 'incident_key')

        # Deleting field 'StorageData.maximum_size'
        db.delete_column('gnmpagerduty_storagedata', 'maximum_size')


    def backwards(self, orm):
        # Adding field 'StorageData.current_size'
        db.add_column('gnmpagerduty_storagedata', 'current_size',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'StorageData.incident_key'
        db.add_column('gnmpagerduty_storagedata', 'incident_key',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True),
                      keep_default=False)

        # Adding field 'StorageData.maximum_size'
        db.add_column('gnmpagerduty_storagedata', 'maximum_size',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)


    models = {
        'gnmpagerduty.incidentkeys': {
            'Meta': {'object_name': 'IncidentKeys'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'storage_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'gnmpagerduty.storagedata': {
            'Meta': {'object_name': 'StorageData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'storage_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'trigger_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gnmpagerduty']
