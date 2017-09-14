# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'platform'
        db.create_table('gnmsyndication_platform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=512)),
            ('intention_label', self.gf('django.db.models.fields.CharField')(max_length=512, unique=True, null=True, blank=True)),
            ('uploadstatus_field', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('publicationstatus_field', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('publicationtime_field', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('enabled_icon_url', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('disable_icon_url', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('display_icon_url', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
        ))
        db.send_create_signal('portal.plugins.gnmsyndication', ['platform'])


    def backwards(self, orm):
        # Deleting model 'platform'
        db.delete_table('gnmsyndication_platform')


    models = {
        'portal.plugins.gnmsyndication.platform': {
            'Meta': {'ordering': "['name']", 'object_name': 'platform'},
            'disable_icon_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'display_icon_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'enabled_icon_url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intention_label': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'}),
            'publicationstatus_field': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'publicationtime_field': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'uploadstatus_field': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['portal.plugins.gnmsyndication']