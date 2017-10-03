# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'KinesisTracker.stream_name'
        db.add_column('kinesisresponder_kinesistracker', 'stream_name',
                      self.gf('django.db.models.fields.CharField')(default='none', max_length=255, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'KinesisTracker.stream_name'
        db.delete_column('kinesisresponder_kinesistracker', 'stream_name')


    models = {
        'portal.plugins.kinesisresponder.kinesistracker': {
            'Meta': {'object_name': 'KinesisTracker'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'exception_trace': ('django.db.models.fields.CharField', [], {'max_length': '32768', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_exception': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'millis_behind_latest': ('django.db.models.fields.BigIntegerField', [], {}),
            'processing_host': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'sequence_number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shard_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stream_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['portal.plugins.kinesisresponder']