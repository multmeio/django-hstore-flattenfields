# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DynamicFieldGroup'
        db.create_table('hstore_flattenfields_dynamicfieldgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=100, separator='_', blank=True, unique=True, populate_from='name', overwrite=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hstore_flattenfields', ['DynamicFieldGroup'])

        # Adding model 'ContentPane'
        db.create_table('hstore_flattenfields_contentpane', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=100, separator='_', blank=True, unique=True, populate_from='name', overwrite=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='content_panes', null=True, to=orm['hstore_flattenfields.DynamicFieldGroup'])),
        ))
        db.send_create_signal('hstore_flattenfields', ['ContentPane'])

        # Adding model 'DynamicField'
        db.create_table('hstore_flattenfields_dynamicfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('refer', self.gf('django.db.models.fields.CharField')(max_length=120, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=120, db_index=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('typo', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('max_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('blank', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('choices', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('html_attrs', self.gf('django_orm.postgresql.hstore.fields.DictionaryField')(db_index=True, null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='dynamic_fields', null=True, to=orm['hstore_flattenfields.DynamicFieldGroup'])),
            ('content_pane', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='dynamic_fields', null=True, to=orm['hstore_flattenfields.ContentPane'])),
        ))
        db.send_create_signal('hstore_flattenfields', ['DynamicField'])


    def backwards(self, orm):
        # Deleting model 'DynamicFieldGroup'
        db.delete_table('hstore_flattenfields_dynamicfieldgroup')

        # Deleting model 'ContentPane'
        db.delete_table('hstore_flattenfields_contentpane')

        # Deleting model 'DynamicField'
        db.delete_table('hstore_flattenfields_dynamicfield')


    models = {
        'hstore_flattenfields.contentpane': {
            'Meta': {'ordering': "['order', 'slug']", 'object_name': 'ContentPane'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'content_panes'", 'null': 'True', 'to': "orm['hstore_flattenfields.DynamicFieldGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '100', 'separator': "'_'", 'blank': 'True', 'unique': 'True', 'populate_from': "'name'", 'overwrite': 'True'})
        },
        'hstore_flattenfields.dynamicfield': {
            'Meta': {'object_name': 'DynamicField'},
            'blank': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'choices': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_pane': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dynamic_fields'", 'null': 'True', 'to': "orm['hstore_flattenfields.ContentPane']"}),
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dynamic_fields'", 'null': 'True', 'to': "orm['hstore_flattenfields.DynamicFieldGroup']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'html_attrs': ('django_orm.postgresql.hstore.fields.DictionaryField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'refer': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'typo': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'hstore_flattenfields.dynamicfieldgroup': {
            'Meta': {'object_name': 'DynamicFieldGroup'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '100', 'separator': "'_'", 'blank': 'True', 'unique': 'True', 'populate_from': "'name'", 'overwrite': 'True'})
        }
    }

    complete_apps = ['hstore_flattenfields']