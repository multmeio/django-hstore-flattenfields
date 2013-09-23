#!/usr/bin/env python
# encoding: utf-8
"""
fields.py

Created by Luan Fonseca de Farias on 2013-09-23.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.db import models
from django_orm.postgresql.hstore import HStoreManager

from hstore_flattenfields.models.queryset import FlattenFieldsFilterQuerySet

class FlattenFieldsFilterManager(HStoreManager):
    def get_query_set(self):
        return FlattenFieldsFilterQuerySet(model=self.model, using=self._db)


class CacheDynamicFieldManager(models.Manager):
    def find_dfields(self, refer=None, name=None, cpane=None, group=None):
        from hstore_flattenfields.models import dfields
        global dfields
        
        def by_refer(x): return x.refer == refer
        def by_name(x): return x.name == name
        def by_cpane(x): return x.content_pane == cpane
        def by_group(x):
            if hasattr(group, 'dynamicfieldgroup_ptr'):
                return x.group == group.dynamicfieldgroup_ptr
            return x.group == group
        def by_refer_group(x): return by_refer(x) and by_group(x)
        def by_refer_cpane(x): return by_refer(x) and by_cpane(x)
        def by_refer_name(x): return by_refer(x) and by_name(x)

        if refer and name:
            return filter(by_refer_name, dfields)
        elif refer and group:
            return filter(by_refer_group, dfields)
        elif refer and cpane:
            return filter(by_refer_cpane, dfields)
        elif name:
            return filter(by_name, dfields)
        elif cpane:
            return filter(by_cpane, dfields)
        elif group:
            return filter(by_group, dfields)
        elif refer:
            return filter(by_refer, dfields)
        else:
            return dfields
