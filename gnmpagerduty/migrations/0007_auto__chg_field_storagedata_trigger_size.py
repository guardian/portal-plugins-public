# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'StorageData.trigger_size'
        db.alter_column('gnmpagerduty_storagedata', 'trigger_size', self.gf('django.db.models.fields.BigIntegerField')(default=1))

    def backwards(self, orm):

        # Changing field 'StorageData.trigger_size'
        db.alter_column('gnmpagerduty_storagedata', 'trigger_size', self.gf('django.db.models.fields.BigIntegerField')(null=True))

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
            'trigger_size': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['gnmpagerduty']