# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'datasource'
        db.create_table('gnmzeitgeist_datasource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('vs_field', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value_mapping_id', self.gf('django.db.models.fields.CharField')(max_length=32768)),
        ))
        db.send_create_signal('portal.plugins.gnmzeitgeist', ['datasource'])


    def backwards(self, orm):
        # Deleting model 'datasource'
        db.delete_table('gnmzeitgeist_datasource')


    models = {
        'portal.plugins.gnmzeitgeist.datasource': {
            'Meta': {'ordering': "['name']", 'object_name': 'datasource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_mapping_id': ('django.db.models.fields.CharField', [], {'max_length': '32768'}),
            'vs_field': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['portal.plugins.gnmzeitgeist']