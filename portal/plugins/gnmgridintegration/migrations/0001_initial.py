# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GridMetadataFields'
        db.create_table('gnmgridintegration_gridmetadatafields', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('grid_field_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('format_string', self.gf('django.db.models.fields.CharField')(max_length=4096)),
            ('vs_field', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('portal.plugins.gnmgridintegration', ['GridMetadataFields'])


    def backwards(self, orm):
        # Deleting model 'GridMetadataFields'
        db.delete_table('gnmgridintegration_gridmetadatafields')


    models = {
        'portal.plugins.gnmgridintegration.gridmetadatafields': {
            'Meta': {'ordering': "['grid_field_name']", 'object_name': 'GridMetadataFields'},
            'format_string': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'grid_field_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'vs_field': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['portal.plugins.gnmgridintegration']