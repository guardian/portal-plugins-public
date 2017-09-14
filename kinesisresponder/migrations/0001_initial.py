# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KinesisTracker'
        db.create_table('kinesisresponder_kinesistracker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shard_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sequence_number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('processing_host', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('millis_behind_latest', self.gf('django.db.models.fields.BigIntegerField')()),
            ('last_exception', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True)),
            ('exception_trace', self.gf('django.db.models.fields.CharField')(max_length=32768, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('kinesisresponder', ['KinesisTracker'])


    def backwards(self, orm):
        # Deleting model 'KinesisTracker'
        db.delete_table('kinesisresponder_kinesistracker')


    models = {
        'kinesisresponder.kinesistracker': {
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
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['kinesisresponder']