# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ImportJob'
        db.create_table('gnmatomresponder_importjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item_id', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('job_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('completed_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('gnmatomresponder', ['ImportJob'])


    def backwards(self, orm):
        # Deleting model 'ImportJob'
        db.delete_table('gnmatomresponder_importjob')


    models = {
        'gnmatomresponder.importjob': {
            'Meta': {'ordering': "['-started_at']", 'object_name': 'ImportJob'},
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['gnmatomresponder']