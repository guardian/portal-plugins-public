# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OutputTimings'
        db.create_table('gnmuploadprofiler_outputtimings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('proxy_completed_interval', self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True)),
            ('page_created_interval', self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True)),
            ('final_transcode_completed_interval', self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True)),
            ('page_launch_guess_interval', self.gf('django.db.models.fields.FloatField')(default=0.0, blank=True)),
            ('completed_time', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('portal.plugins.gnmuploadprofiler', ['OutputTimings'])


    def backwards(self, orm):
        # Deleting model 'OutputTimings'
        db.delete_table('gnmuploadprofiler_outputtimings')


    models = {
        'portal.plugins.gnmuploadprofiler.outputtimings': {
            'Meta': {'object_name': 'OutputTimings'},
            'completed_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {}),
            'final_transcode_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'page_created_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'page_launch_guess_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'proxy_completed_interval': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        }
    }

    complete_apps = ['portal.plugins.gnmuploadprofiler']