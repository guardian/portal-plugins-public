# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ImportJob.atom_title'
        db.add_column('gnmatomresponder_importjob', 'atom_title',
                      self.gf('django.db.models.fields.CharField')(default='Unknown title', max_length=1024),
                      keep_default=False)

        # Adding field 'ImportJob.user_email'
        db.add_column('gnmatomresponder_importjob', 'user_email',
                      self.gf('django.db.models.fields.CharField')(default='Unknow user', max_length=1024, db_index=True),
                      keep_default=False)

        # Adding field 'ImportJob.s3_path'
        db.add_column('gnmatomresponder_importjob', 's3_path',
                      self.gf('django.db.models.fields.CharField')(max_length=2048, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ImportJob.atom_title'
        db.delete_column('gnmatomresponder_importjob', 'atom_title')

        # Deleting field 'ImportJob.user_email'
        db.delete_column('gnmatomresponder_importjob', 'user_email')

        # Deleting field 'ImportJob.s3_path'
        db.delete_column('gnmatomresponder_importjob', 's3_path')


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
        }
    }

    complete_apps = ['gnmatomresponder']