# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'settings'
        db.create_table('gnmyoutube_settings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=32768)),
        ))
        db.send_create_signal('portal.plugins.gnmyoutube', ['settings'])


    def backwards(self, orm):
        # Deleting model 'settings'
        db.delete_table('gnmyoutube_settings')


    models = {
        'portal.plugins.gnmyoutube.settings': {
            'Meta': {'object_name': 'settings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32768'})
        }
    }

    complete_apps = ['portal.plugins.gnmyoutube']