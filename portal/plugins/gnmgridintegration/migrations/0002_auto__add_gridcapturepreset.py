# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GridCapturePreset'
        db.create_table('gnmgridintegration_gridcapturepreset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vs_field', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('field_value_regex', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('portal.plugins.gnmgridintegration', ['GridCapturePreset'])


    def backwards(self, orm):
        # Deleting model 'GridCapturePreset'
        db.delete_table('gnmgridintegration_gridcapturepreset')


    models = {
        'portal.plugins.gnmgridintegration.gridcapturepreset': {
            'Meta': {'ordering': "['vs_field', 'field_value_regex']", 'object_name': 'GridCapturePreset'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'field_value_regex': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vs_field': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'portal.plugins.gnmgridintegration.gridmetadatafields': {
            'Meta': {'ordering': "['type', 'grid_field_name']", 'object_name': 'GridMetadataFields'},
            'format_string': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'grid_field_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'vs_field': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['portal.plugins.gnmgridintegration']