#!/usr/bin/env python
# encoding: utf-8

"""
hstore_flattenfields.cache
-------------

The Cache module where places all the function and
classes used to store the structure and data from
hstore_flattenfields application.

:copyright: 2013, multmeio (http://www.multmeio.com.br)
:author: 2013, Luan Fonseca <luanfonceca@gmail.com>
:license: BSD, see LICENSE for more details.
"""

from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase

class TestCase(TestCase):
    """
    Class Created to override the normal behaviour of
    the TestCase's Django Class and clean the cache
    after each test.
    """
    def tearDown(self):
        if getattr(settings, 'CACHES', False):
            cache.clear()
        super(TestCase, self).tearDown()


class BaseCacheManager(models.Manager):
    def __init__(self, *args, **kwargs):
        if 'cache_key' in kwargs:
            self.cache_key = kwargs.pop('cache_key')
            self.select_args = kwargs.pop('select_related', [])
            self.prefetch_args = kwargs.pop('prefetch_related', [])
        super(BaseCacheManager, self).__init__(*args, **kwargs)

    def contribute_to_class(self, model, name):
        super(BaseCacheManager, self).contribute_to_class(model, name)
        models.signals.post_save.connect(self.charge_cache, model)
        models.signals.post_delete.connect(self.charge_cache, model)

    @property
    def cached_data(self):
        return cache.get(self.cache_key, [])

    def charge_cache(self, **kwargs):
        cache.set(self.cache_key,
            self.model.objects\
                .select_related(*self.select_args)\
                .prefetch_related(*self.prefetch_args)
        )

    def cache_filter(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must define this method.')


class DynamicFieldCacheManager(BaseCacheManager):
    def cache_filter(self, refer=None, name=None, cpane=None, group=None):
        def by_refer(x):
            return x.refer == refer

        def by_name(x):
            return x.name == name

        def by_cpane(x):
            return x.content_pane == cpane

        def by_group(x):
            if hasattr(group, 'dynamicfieldgroup_ptr'):
                return x.group == group.dynamicfieldgroup_ptr
            return x.group == group

        def by_refer_group(x):
            return by_refer(x) and by_group(x)

        def by_refer_cpane(x):
            return by_refer(x) and by_cpane(x)

        def by_refer_name(x):
            return by_refer(x) and by_name(x)

        if refer and name:
            return filter(by_refer_name, self.cached_data)
        elif refer and group:
            return filter(by_refer_group, self.cached_data)
        elif refer and cpane:
            return filter(by_refer_cpane, self.cached_data)
        elif name:
            return filter(by_name, self.cached_data)
        elif cpane:
            return filter(by_cpane, self.cached_data)
        elif group:
            return filter(by_group, self.cached_data)
        elif refer:
            return filter(by_refer, self.cached_data)
        else:
            return self.cached_data


class ContentPaneCacheManager(BaseCacheManager):
    def cache_filter(self, name=None, group=None, model=None):
        def by_name(x):
            return x.name == name

        def by_model(x):
            return x.content_type and x.content_type.model == model

        def by_group(x):
            return x.group == group

        if name:
            return filter(by_name, self.cached_data)
        elif model:
            return filter(by_model, self.cached_data)
        elif group:
            return filter(by_group, self.cached_data)
        else:
            return self.cached_data

class DynamicFieldGroupCacheManager(BaseCacheManager):
    def cache_filter(self, name=None, ctype=None):
        def by_name(x):
            return x.name == name

        if name:
            return filter(by_name, self.cached_data)
        else:
            return self.cached_data
