# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProjectSizeInfoModel'
        db.create_table('gnmplutostats_projectsizeinfomodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, db_index=True)),
            ('storage_id', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('size_used_gb', self.gf('django.db.models.fields.IntegerField')()),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('gnmplutostats', ['ProjectSizeInfoModel'])

        # Adding unique constraint on 'ProjectSizeInfoModel', fields ['project_id', 'storage_id']
        db.create_unique('gnmplutostats_projectsizeinfomodel', ['project_id', 'storage_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProjectSizeInfoModel', fields ['project_id', 'storage_id']
        db.delete_unique('gnmplutostats_projectsizeinfomodel', ['project_id', 'storage_id'])

        # Deleting model 'ProjectSizeInfoModel'
        db.delete_table('gnmplutostats_projectsizeinfomodel')


    models = {
        'gnmplutostats.projectsizeinfomodel': {
            'Meta': {'unique_together': "(('project_id', 'storage_id'),)", 'object_name': 'ProjectSizeInfoModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'project_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'db_index': 'True'}),
            'size_used_gb': ('django.db.models.fields.IntegerField', [], {}),
            'storage_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        }
    }

    complete_apps = ['gnmplutostats']