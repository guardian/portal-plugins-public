# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PacFormXml'
        db.create_table('gnmatomresponder_pacformxml', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('atom_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('received', self.gf('django.db.models.fields.DateTimeField')()),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pacdata_url', self.gf('django.db.models.fields.CharField')(max_length=4096)),
            ('status', self.gf('django.db.models.fields.CharField')(default='UNPROCESSED', max_length=32, db_index=True)),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, db_index=True)),
            ('last_error', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('gnmatomresponder', ['PacFormXml'])


    def backwards(self, orm):
        # Deleting model 'PacFormXml'
        db.delete_table('gnmatomresponder_pacformxml')


    models = {
        'gnmatomresponder.importjob': {
            'Meta': {'ordering': "['-started_at']", 'object_name': 'ImportJob'},
            'atom_title': ('django.db.models.fields.CharField', [], {'default': "'Unknown title'", 'max_length': '1024'}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            's3_path': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user_email': ('django.db.models.fields.CharField', [], {'default': "'Unknow user'", 'max_length': '1024', 'db_index': 'True'})
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