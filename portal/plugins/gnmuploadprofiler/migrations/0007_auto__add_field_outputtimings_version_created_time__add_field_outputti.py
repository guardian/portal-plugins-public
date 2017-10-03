# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OutputTimings.version_created_time'
        db.add_column('gnmuploadprofiler_outputtimings', 'version_created_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2016, 5, 6, 0, 0)),
                      keep_default=False)

        # Adding field 'OutputTimings.media_version'
        db.add_column('gnmuploadprofiler_outputtimings', 'media_version',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'OutputTimings.version_created_time'
        db.delete_column('gnmuploadprofiler_outputtimings', 'version_created_time')

        # Deleting field 'OutputTimings.media_version'
        db.delete_column('gnmuploadprofiler_outputtimings', 'media_version')


    models = {
        'portal.plugins.gnmuploadprofiler.outputtimings': {
            'Meta': {'ordering': "['-completed_time', '-created_time']", 'object_name': 'OutputTimings'},
            'capi_page_created_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'completed_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {}),
            'final_transcode_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_duration': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'item_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'media_version': ('django.db.models.fields.IntegerField', [], {}),
            'page_created_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_capi_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_guess_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_pluto_lag': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'proxy_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'upload_trigger_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'version_created_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['portal.plugins.gnmuploadprofiler']