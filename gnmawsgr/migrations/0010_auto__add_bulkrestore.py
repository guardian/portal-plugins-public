# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BulkRestore'
        db.create_table('gnmawsgr_bulkrestore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent_collection', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('username', self.gf('django.db.models.fields.CharField')(default='admin', max_length=512)),
            ('number_requested', self.gf('django.db.models.fields.IntegerField')()),
            ('number_queued', self.gf('django.db.models.fields.IntegerField')()),
            ('number_already_going', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('gnmawsgr', ['BulkRestore'])


    def backwards(self, orm):
        # Deleting model 'BulkRestore'
        db.delete_table('gnmawsgr_bulkrestore')


    models = {
        'gnmawsgr.bulkrestore': {
            'Meta': {'object_name': 'BulkRestore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_already_going': ('django.db.models.fields.IntegerField', [], {}),
            'number_queued': ('django.db.models.fields.IntegerField', [], {}),
            'number_requested': ('django.db.models.fields.IntegerField', [], {}),
            'parent_collection': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '512'})
        },
        'gnmawsgr.restorerequest': {
            'Meta': {'ordering': "['-requested_at', '-completed_at', 'username', '-item_id']", 'object_name': 'RestoreRequest'},
            'attempts': ('django.db.models.fields.IntegerField', [], {}),
            'completed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'currently_downloaded': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'failure_reason': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True', 'blank': 'True'}),
            'file_size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'file_size_check': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'filepath_destination': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'filepath_original': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent_collection': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'project_id': ('django.db.models.fields.CharField', [], {'default': "'(unknown)'", 'max_length': '32'}),
            'requested_at': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '512'})
        }
    }

    complete_apps = ['gnmawsgr']