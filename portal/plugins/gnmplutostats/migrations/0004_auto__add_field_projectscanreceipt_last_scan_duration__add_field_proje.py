# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ProjectScanReceipt.last_scan_duration'
        db.add_column('gnmplutostats_projectscanreceipt', 'last_scan_duration',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'ProjectScanReceipt.last_scan_error'
        db.add_column('gnmplutostats_projectscanreceipt', 'last_scan_error',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=4096, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ProjectScanReceipt.last_scan_duration'
        db.delete_column('gnmplutostats_projectscanreceipt', 'last_scan_duration')

        # Deleting field 'ProjectScanReceipt.last_scan_error'
        db.delete_column('gnmplutostats_projectscanreceipt', 'last_scan_error')


    models = {
        'gnmplutostats.projectscanreceipt': {
            'Meta': {'object_name': 'ProjectScanReceipt'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scan': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_scan_duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'last_scan_error': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'project_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'project_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'project_title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
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