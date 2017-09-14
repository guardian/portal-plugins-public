# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'datasource.value_mapping_id'
        db.alter_column('gnmzeitgeist_datasource', 'value_mapping_id', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True))

    def backwards(self, orm):

        # Changing field 'datasource.value_mapping_id'
        db.alter_column('gnmzeitgeist_datasource', 'value_mapping_id', self.gf('django.db.models.fields.CharField')(default='', max_length=32768))

    models = {
        'portal.plugins.gnmzeitgeist.datasource': {
            'Meta': {'ordering': "['name']", 'object_name': 'datasource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_mapping_id': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True', 'blank': 'True'}),
            'vs_field': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['portal.plugins.gnmzeitgeist']