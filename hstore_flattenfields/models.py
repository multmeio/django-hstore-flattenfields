#!/usr/bin/env python
# encoding: utf-8

'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models, connection
from django_orm.postgresql import hstore
from django.utils.datastructures import SortedDict
from django import forms

import json

# import caching.base
import copy

from fields import *
from utils import single_list_to_tuple


dfields = None

class DynamicField(models.Model):
    refer = models.CharField(max_length=120, blank=False, db_index=True, verbose_name="Class name")
    name = models.CharField(max_length=120, blank=False, db_index=True, verbose_name="Field name")
    verbose_name = models.CharField(max_length=120, blank=False, verbose_name="Verbose name")
    typo = models.CharField(max_length=20, blank=False, db_index=True, verbose_name="Field type",
        choices=single_list_to_tuple(FIELD_TYPES))
    max_length = models.IntegerField(null=True, blank=True, verbose_name="Length")
    blank = models.BooleanField(default=True, verbose_name="Blank")
    choices = models.TextField(null=True, blank=True, verbose_name="Choices")
    default_value = models.CharField(max_length=80, null=True, blank=True, verbose_name="Default value")

    class Meta:
        db_table = u'dynamic_field'

    def __unicode__(self):
        return self.verbose_name or self.name

    @property
    def has_blank_option(self):
        return self.blank and \
            self.typo not in FIELD_TYPES_WITHOUT_BLANK_OPTION

    def save(self, *args, **kwargs):
        super(DynamicField, self).save(*args, **kwargs)
        # NOTE: force update global dfields resultset
        global dfields
        dfields =  DynamicField.objects.all()


# XXX: Charge memory with all dfields for prevent flood on db.
# NOTE: this solution need to restart project on each new dfield add. Nasty!!
dfields =  DynamicField.objects.all()

def find_dfields(refer, name=None):
    if name:
        return [dfield for dfield in dfields \
            if dfield.refer == refer and dfield.name == name]
    return [dfield for dfield in dfields if dfield.refer == refer]

# NOTE: Error happen on syncdb, because DynamicField's table does not exist.
cursor = connection.cursor()
cursor.execute("select count(*) from pg_tables where tablename='dynamic_field'")
DYNAMIC_FIELD_TABLE_EXIST = (cursor.fetchone()[0] > 0)


class HStoreModelMeta(models.Model.__metaclass__):
    def __new__(cls, name, bases, attrs):
        super_new = super(HStoreModelMeta, cls).__new__

        # create it
        new_class = super_new(cls, name, bases, attrs)

        # pos create

        # override getattr/setattr/delattr
        old_getattribute = new_class.__getattribute__
        def __getattribute__(self, key):
            if key.startswith('_') and key.endswith('_cache'):
                return None

            try:
                return old_getattribute(self, key)
            except AttributeError:
                if hasattr(self, '_dfields') and key in self._dfields:
                    return self._dfields[key]
                raise

        new_class.__getattribute__ = __getattribute__

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            #print "called __setattr__(%r, %r)" % (key, value)

            if hasattr(self, '_dfields') and not key in dir(new_class):
                # XXX: search for key on table, django will call this method many times on __init__
                new_class_refer = new_class.__name__
                # if DynamicField.objects.filter(refer=new_class_refer, name=key).exists():
                if find_dfields(refer=new_class_refer, name=key):
                    if isinstance(value, (list, tuple)):
                        value = [unicode(v) for v in value]
                    elif value is not None:
                        value = unicode(value)
                    self._dfields[key] = unicode(value)
                    return

            old_setattr(self, key, value)

        new_class.__setattr__ = __setattr__

        old_delattr = new_class.__delattr__
        def __delattr__(self, key):
            if hasattr(self, '_dfields') and not key in dir(new_class):
                if key in self._dfields:
                    del self._dfields[key]
                    return

            return old_delattr(self, key)
        new_class.__delattr__ = __delattr__

        # override _meta.fields (property)
        _old_meta = new_class._meta
        class _meta(object):
            @property
            def dynamic_fields(self):
                fields = []
                if not DYNAMIC_FIELD_TABLE_EXIST:
                    return fields

                # metafields = DynamicField.objects.filter(refer=new_class.__name__)
                metafields = find_dfields(refer=new_class.__name__)
                for metafield in metafields:
                    try:
                        field_klass_name = FIELD_TYPES_DICT.get(metafield.typo,
                                                                FIELD_TYPE_DEFAULT)

                        #FIXME: eval is the evil, use module package
                        field_klass = eval(field_klass_name)
                        if metafield.choices == '':
                            choices_ = None
                        else:
                            choices_ = single_list_to_tuple([\
                                s.strip() for s in metafield.choices.splitlines()
                            ])

                        field = field_klass(name=metafield.name,
                                            max_length=metafield.max_length or 255,
                                            choices=choices_,
                                            default=metafield.default_value,
                                            verbose_name=metafield.verbose_name,
                                            blank=metafield.blank,
                                            null=True)
                        field.attname = metafield.name
                        fields.append(field)
                    except:
                        raise \
                            TypeError(('Cannot create field for %r, maybe type %r ' + \
                                       'is not a django type') % (metafield, field_klass_name))
                return fields

            def __eq__(self, other):
                return _old_meta == other

            @property
            def fields(self):
                #add dynamic_fields from table
                return _old_meta.fields + self.dynamic_fields

            def __getattr__(self, key):
                return getattr(_old_meta, key)
            def __setattr__(self, key, value):
                return setattr(_old_meta, key, value)
        new_class._meta = _meta()

        # return it
        return new_class

class HStoreModel(models.Model):
    __metaclass__ = HStoreModelMeta
    objects = hstore.HStoreManager()
    _dfields = hstore.DictionaryField(db_index=True, null=True, blank=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        _dfields = None
        if args:
            # XXX: hack in order to save _dfields without alter django
            # save _dfields in args and restore

            # what the index of _dfields?
            i = 0
            index = None
            for f in self._meta.local_fields:
                if f.name == "_dfields":
                    index = i
                    break
                i = i + 1
            if index is not None and index < len(args):
                _dfields = args[index]

        super(HStoreModel, self).__init__(*args, **kwargs)
        if _dfields:
            self._dfields = _dfields
