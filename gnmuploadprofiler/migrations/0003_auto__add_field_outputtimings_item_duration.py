# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OutputTimings.item_duration'
        db.add_column('gnmuploadprofiler_outputtimings', 'item_duration',
                      self.gf('django.db.models.fields.FloatField')(default=0.0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'OutputTimings.item_duration'
        db.delete_column('gnmuploadprofiler_outputtimings', 'item_duration')


    models = {
        'gnmuploadprofiler.outputtimings': {
            'Meta': {'object_name': 'OutputTimings'},
            'completed_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {}),
            'final_transcode_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_duration': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'item_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'page_created_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_guess_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'proxy_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'upload_trigger_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        }
    }

    complete_apps = ['gnmuploadprofiler']