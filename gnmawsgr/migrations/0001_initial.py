# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RestoreRequest'
        db.create_table('gnmawsgr_restorerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('requested_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('completed_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('attempts', self.gf('django.db.models.fields.IntegerField')()),
            ('item_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('gnmawsgr', ['RestoreRequest'])


    def backwards(self, orm):
        # Deleting model 'RestoreRequest'
        db.delete_table('gnmawsgr_restorerequest')


    models = {
        'gnmawsgr.restorerequest': {
            'Meta': {'object_name': 'RestoreRequest'},
            'attempts': ('django.db.models.fields.IntegerField', [], {}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'requested_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['gnmawsgr']