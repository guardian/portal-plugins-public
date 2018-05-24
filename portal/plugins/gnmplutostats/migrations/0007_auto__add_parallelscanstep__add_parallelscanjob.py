# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ParallelScanStep'
        db.create_table('gnmplutostats_parallelscanstep', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('master_job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gnmplutostats.ParallelScanJob'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('took', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('search_param', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True)),
            ('last_error', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True)),
            ('retry_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('start_at', self.gf('django.db.models.fields.IntegerField')()),
            ('end_at', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gnmplutostats', ['ParallelScanStep'])

        # Adding model 'ParallelScanJob'
        db.create_table('gnmplutostats_parallelscanjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job_desc', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True)),
            ('last_error', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True)),
            ('items_to_scan', self.gf('django.db.models.fields.IntegerField')()),
            ('pages', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gnmplutostats', ['ParallelScanJob'])


    def backwards(self, orm):
        # Deleting model 'ParallelScanStep'
        db.delete_table('gnmplutostats_parallelscanstep')

        # Deleting model 'ParallelScanJob'
        db.delete_table('gnmplutostats_parallelscanjob')


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
        'gnmplutostats.parallelscanjob': {
            'Meta': {'object_name': 'ParallelScanJob'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_to_scan': ('django.db.models.fields.IntegerField', [], {}),
            'job_desc': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'last_error': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'gnmplutostats.parallelscanstep': {
            'Meta': {'object_name': 'ParallelScanStep'},
            'end_at': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_error': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'master_job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gnmplutostats.ParallelScanJob']"}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'retry_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'search_param': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'start_at': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'took': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
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