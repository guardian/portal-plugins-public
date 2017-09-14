# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LibraryNickname'
        db.create_table('gnmlibrarytool_librarynickname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('library_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=254)),
        ))
        db.send_create_signal('portal.plugins.gnmlibrarytool', ['LibraryNickname'])


    def backwards(self, orm):
        # Deleting model 'LibraryNickname'
        db.delete_table('gnmlibrarytool_librarynickname')


    models = {
        'portal.plugins.gnmlibrarytool.librarynickname': {
            'Meta': {'object_name': 'LibraryNickname'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '254'})
        }
    }

    complete_apps = ['portal.plugins.gnmlibrarytool']