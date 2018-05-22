# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CategoryScanInfo'
        db.create_table('gnmplutostats_categoryscaninfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category_label', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('storage_id', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('attached', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('size_used_gb', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gnmplutostats', ['CategoryScanInfo'])

        # Adding unique constraint on 'CategoryScanInfo', fields ['last_updated', 'category_label', 'storage_id', 'attached']
        db.create_unique('gnmplutostats_categoryscaninfo', ['last_updated', 'category_label', 'storage_id', 'attached'])


    def backwards(self, orm):
        # Removing unique constraint on 'CategoryScanInfo', fields ['last_updated', 'category_label', 'storage_id', 'attached']
        db.delete_unique('gnmplutostats_categoryscaninfo', ['last_updated', 'category_label', 'storage_id', 'attached'])

        # Deleting model 'CategoryScanInfo'
        db.delete_table('gnmplutostats_categoryscaninfo')


    models = {
        'gnmplutostats.categoryscaninfo': {
            'Meta': {'unique_together': "(('last_updated', 'category_label', 'storage_id', 'attached'),)", 'object_name': 'CategoryScanInfo'},
            'attached': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category_label': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
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