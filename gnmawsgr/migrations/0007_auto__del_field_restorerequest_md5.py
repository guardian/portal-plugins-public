# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'RestoreRequest.md5'
        db.delete_column('gnmawsgr_restorerequest', 'md5')


    def backwards(self, orm):
        # Adding field 'RestoreRequest.md5'
        db.add_column('gnmawsgr_restorerequest', 'md5',
                      self.gf('django.db.models.fields.CharField')(max_length=32768, null=True),
                      keep_default=False)


    models = {
        'gnmawsgr.restorerequest': {
            'Meta': {'object_name': 'RestoreRequest'},
            'attempts': ('django.db.models.fields.IntegerField', [], {}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'currently_downloaded': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'failure_reason': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True', 'blank': 'True'}),
            'file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'filepath_destination': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'filepath_original': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent_collection': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'project_id': ('django.db.models.fields.CharField', [], {'default': "'(unknown)'", 'max_length': '32'}),
            'requested_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '512'})
        }
    }

    complete_apps = ['gnmawsgr']