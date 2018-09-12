# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ImportJob.processing'
        db.add_column('gnmatomresponder_importjob', 'processing',
                      self.gf('django.db.models.fields.BooleanField')(default=False))

    def backwards(self, orm):
        # Deleting field 'ImportJob.processing'
        db.delete_column('gnmatomresponder_importjob', 'processing')


    models = {
        'gnmatomresponder.importjob': {
            'Meta': {'ordering': "['-started_at']", 'object_name': 'ImportJob'},
            'atom_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'atom_title': ('django.db.models.fields.CharField', [], {'default': "'Unknown title'", 'max_length': '1024'}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'processing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'retry_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            's3_path': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user_email': ('django.db.models.fields.CharField', [], {'default': "'Unknown user'", 'max_length': '1024', 'db_index': 'True'})
        },
        'gnmatomresponder.pacformxml': {
            'Meta': {'object_name': 'PacFormXml'},
            'atom_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'celery_task_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'db_index': 'True'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_error': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pacdata_url': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'received': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'UNPROCESSED'", 'max_length': '32', 'db_index': 'True'})
        }
    }

    complete_apps = ['gnmatomresponder']