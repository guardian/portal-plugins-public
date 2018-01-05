# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DownloadableLink.s3_url'
        db.add_column('gnmdownloadablelink_downloadablelink', 's3_url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True),
                      keep_default=False)

        # Adding index on 'DownloadableLink', fields ['status']
        db.create_index('gnmdownloadablelink_downloadablelink', ['status'])

        # Adding index on 'DownloadableLink', fields ['item_id']
        db.create_index('gnmdownloadablelink_downloadablelink', ['item_id'])

        # Adding index on 'DownloadableLink', fields ['shapetag']
        db.create_index('gnmdownloadablelink_downloadablelink', ['shapetag'])

        # Adding unique constraint on 'DownloadableLink', fields ['item_id', 'shapetag']
        db.create_unique('gnmdownloadablelink_downloadablelink', ['item_id', 'shapetag'])


    def backwards(self, orm):
        # Removing unique constraint on 'DownloadableLink', fields ['item_id', 'shapetag']
        db.delete_unique('gnmdownloadablelink_downloadablelink', ['item_id', 'shapetag'])

        # Removing index on 'DownloadableLink', fields ['shapetag']
        db.delete_index('gnmdownloadablelink_downloadablelink', ['shapetag'])

        # Removing index on 'DownloadableLink', fields ['item_id']
        db.delete_index('gnmdownloadablelink_downloadablelink', ['item_id'])

        # Removing index on 'DownloadableLink', fields ['status']
        db.delete_index('gnmdownloadablelink_downloadablelink', ['status'])

        # Deleting field 'DownloadableLink.s3_url'
        db.delete_column('gnmdownloadablelink_downloadablelink', 's3_url')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gnmdownloadablelink.downloadablelink': {
            'Meta': {'unique_together': "(('item_id', 'shapetag'),)", 'object_name': 'DownloadableLink'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'expiry': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'public_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            's3_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'shapetag': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'transcode_job': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        }
    }

    complete_apps = ['gnmdownloadablelink']