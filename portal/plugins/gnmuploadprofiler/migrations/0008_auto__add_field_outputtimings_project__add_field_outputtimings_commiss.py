# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OutputTimings.project'
        db.add_column('gnmuploadprofiler_outputtimings', 'project',
                      self.gf('django.db.models.fields.CharField')(db_index=True, default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'OutputTimings.commission'
        db.add_column('gnmuploadprofiler_outputtimings', 'commission',
                      self.gf('django.db.models.fields.CharField')(db_index=True, default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'OutputTimings.project'
        db.delete_column('gnmuploadprofiler_outputtimings', 'project')

        # Deleting field 'OutputTimings.commission'
        db.delete_column('gnmuploadprofiler_outputtimings', 'commission')


    models = {
        'portal.plugins.gnmuploadprofiler.outputtimings': {
            'Meta': {'ordering': "['-completed_time', '-created_time']", 'object_name': 'OutputTimings'},
            'capi_page_created_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'commission': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
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
            'project': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'proxy_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'upload_trigger_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'version_created_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['portal.plugins.gnmuploadprofiler']