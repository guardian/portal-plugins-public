# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProjectScanReceipt'
        db.create_table('gnmplutostats_projectscanreceipt', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('last_scan', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('project_status', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('project_title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('gnmplutostats', ['ProjectScanReceipt'])


    def backwards(self, orm):
        # Deleting model 'ProjectScanReceipt'
        db.delete_table('gnmplutostats_projectscanreceipt')


    models = {
        'gnmplutostats.projectscanreceipt': {
            'Meta': {'object_name': 'ProjectScanReceipt'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scan': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'project_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'project_status': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'project_title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
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