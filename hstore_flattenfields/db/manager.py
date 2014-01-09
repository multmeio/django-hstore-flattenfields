#!/usr/bin/env python
# encoding: utf-8
"""
fields.py

Created by Luan Fonseca de Farias on 2013-09-23.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.db import models
from django_orm.postgresql.hstore import HStoreManager

from hstore_flattenfields.db.queryset import FlattenFieldsFilterQuerySet


class FlattenFieldsFilterManager(HStoreManager):
    def get_query_set(self):
        return FlattenFieldsFilterQuerySet(model=self.model, using=self._db)

    def _insert(self, *args, **kwargs):
        def is_not_dynamic(field):
            return not field.db_type == 'dynamic_field'

        kwargs.update({
            'fields': filter(is_not_dynamic, kwargs.get('fields'))
        })
        return super(FlattenFieldsFilterManager, self)._insert(*args, **kwargs)