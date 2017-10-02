# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StorageData'
        db.create_table('gnmpagerduty_storagedata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('storage_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('maximum_size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('current_size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('trigger_size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('gnmpagerduty', ['StorageData'])


    def backwards(self, orm):
        # Deleting model 'StorageData'
        db.delete_table('gnmpagerduty_storagedata')


    models = {
        'gnmpagerduty.storagedata': {
            'Meta': {'object_name': 'StorageData'},
            'current_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'storage_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'trigger_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['gnmpagerduty']