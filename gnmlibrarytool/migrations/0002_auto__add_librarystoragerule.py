# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LibraryStorageRule'
        db.create_table('gnmlibrarytool_librarystoragerule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('storagerule_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('storagerule_xml_source', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('gnmlibrarytool', ['LibraryStorageRule'])


    def backwards(self, orm):
        # Deleting model 'LibraryStorageRule'
        db.delete_table('gnmlibrarytool_librarystoragerule')


    models = {
        'gnmlibrarytool.librarynickname': {
            'Meta': {'object_name': 'LibraryNickname'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '254'})
        },
        'gnmlibrarytool.librarystoragerule': {
            'Meta': {'object_name': 'LibraryStorageRule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'storagerule_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'storagerule_xml_source': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['gnmlibrarytool']