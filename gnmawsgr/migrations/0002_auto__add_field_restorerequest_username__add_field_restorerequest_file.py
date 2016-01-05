# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'RestoreRequest.username'
        db.add_column('gnmawsgr_restorerequest', 'username',
                      self.gf('django.db.models.fields.CharField')(default='admin', max_length=512),
                      keep_default=False)

        # Adding field 'RestoreRequest.file_size'
        db.add_column('gnmawsgr_restorerequest', 'file_size',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'RestoreRequest.currently_downloaded'
        db.add_column('gnmawsgr_restorerequest', 'currently_downloaded',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'RestoreRequest.project_id'
        db.add_column('gnmawsgr_restorerequest', 'project_id',
                      self.gf('django.db.models.fields.CharField')(default='(unknown)', max_length=32),
                      keep_default=False)

        # Adding field 'RestoreRequest.filepath_original'
        db.add_column('gnmawsgr_restorerequest', 'filepath_original',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32768, blank=True),
                      keep_default=False)

        # Adding field 'RestoreRequest.filepath_destination'
        db.add_column('gnmawsgr_restorerequest', 'filepath_destination',
                      self.gf('django.db.models.fields.CharField')(max_length=32768, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'RestoreRequest.username'
        db.delete_column('gnmawsgr_restorerequest', 'username')

        # Deleting field 'RestoreRequest.file_size'
        db.delete_column('gnmawsgr_restorerequest', 'file_size')

        # Deleting field 'RestoreRequest.currently_downloaded'
        db.delete_column('gnmawsgr_restorerequest', 'currently_downloaded')

        # Deleting field 'RestoreRequest.project_id'
        db.delete_column('gnmawsgr_restorerequest', 'project_id')

        # Deleting field 'RestoreRequest.filepath_original'
        db.delete_column('gnmawsgr_restorerequest', 'filepath_original')

        # Deleting field 'RestoreRequest.filepath_destination'
        db.delete_column('gnmawsgr_restorerequest', 'filepath_destination')


    models = {
        'gnmawsgr.restorerequest': {
            'Meta': {'object_name': 'RestoreRequest'},
            'attempts': ('django.db.models.fields.IntegerField', [], {}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'currently_downloaded': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'filepath_destination': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'filepath_original': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'project_id': ('django.db.models.fields.CharField', [], {'default': "'(unknown)'", 'max_length': '32'}),
            'requested_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '512'})
        }
    }

    complete_apps = ['gnmawsgr']