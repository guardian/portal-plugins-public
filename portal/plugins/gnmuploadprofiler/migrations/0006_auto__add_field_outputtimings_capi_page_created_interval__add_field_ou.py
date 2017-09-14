# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OutputTimings.capi_page_created_interval'
        db.add_column('gnmuploadprofiler_outputtimings', 'capi_page_created_interval',
                      self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True),
                      keep_default=False)

        # Adding field 'OutputTimings.page_launch_pluto_lag'
        db.add_column('gnmuploadprofiler_outputtimings', 'page_launch_pluto_lag',
                      self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'OutputTimings.capi_page_created_interval'
        db.delete_column('gnmuploadprofiler_outputtimings', 'capi_page_created_interval')

        # Deleting field 'OutputTimings.page_launch_pluto_lag'
        db.delete_column('gnmuploadprofiler_outputtimings', 'page_launch_pluto_lag')


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
            'page_created_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_capi_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_guess_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_pluto_lag': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'proxy_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'upload_trigger_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        }
    }

    complete_apps = ['portal.plugins.gnmuploadprofiler']