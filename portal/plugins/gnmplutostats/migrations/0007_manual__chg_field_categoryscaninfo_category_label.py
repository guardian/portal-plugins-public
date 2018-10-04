# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'CategoryScanInfo.category_label'
        db.alter_column('gnmplutostats_categoryscaninfo', 'category_label', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True))

    def backwards(self, orm):

        # Changing field 'CategoryScanInfo.category_label'
        db.alter_column('gnmplutostats_categoryscaninfo', 'category_label', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True))


    models = {
        'gnmplutostats.categoryscaninfo': {
            'Meta': {'unique_together': "(('last_updated', 'category_label', 'storage_id', 'attached'),)", 'object_name': 'CategoryScanInfo'},
            'attached': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category_label': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'size_used_gb': ('django.db.models.fields.IntegerField', [], {}),
            'storage_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'gnmplutostats.projectscanreceipt': {
            'Meta': {'object_name': 'ProjectScanReceipt'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scan': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_scan_duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'last_scan_error': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'project_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'project_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'project_title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'})
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