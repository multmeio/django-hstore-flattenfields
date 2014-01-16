#!/usr/bin/env python
# encoding: utf-8
"""
fields.py

Created by Luan Fonseca de Farias on 2013-09-23.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

import datetime
import numbers
import operator

from django.utils import tree
from django.core.exceptions import FieldError

try:
    from django.db.models.sql.constants import LOOKUP_SEP
except ImportError:
    # FIXME: Changed in django>=1.5
    from django.db.models.constants import LOOKUP_SEP

from django.db.models.fields import FieldDoesNotExist
from django.db.models.sql.where import ExtraWhere
from django.db.models.query import *

from django_orm.core.sql.tree import AND, OR

from hstore_flattenfields.utils import *


class HStoreConstraint():
    def __init__(self, alias, field, value, lookup_type, key=None):
        self.lvalue = '%s'
        self.alias = alias
        self.field = field
        self.values = [value]

        if lookup_type in VALUE_OPERATORS:
            self.operator = VALUE_OPERATORS[lookup_type]

            if lookup_type in SPECIAL_CHARS_OPERATORS and has_any_in(SPECIAL_CHARS, value):
                for char in [x for x in value if x in SPECIAL_CHARS]:
                    value = value.replace(char, '\%s' % char)

            if self.operator == 'IN':
                test_value = value[0]
                self.values = [tuple(value)]
            elif lookup_type in ["contains", "icontains"]:
                test_value = "%%%s%%" % value
                self.values = [test_value]
            elif lookup_type in ["startswith", "istartswith"]:
                test_value = "%s%%" % value
                self.values = [test_value]
            elif lookup_type in ["endswith", "iendswith"]:
                test_value = "%%%s" % value
                self.values = [test_value]
            else:
                test_value = value

            if isinstance(test_value, datetime.datetime):
                cast_type = 'timestamp'
            elif isinstance(test_value, datetime.date):
                cast_type = 'date'
            elif isinstance(test_value, datetime.time):
                cast_type = 'time'
            elif isinstance(test_value, int):
                cast_type = 'integer'
            elif isinstance(test_value, numbers.Number):
                cast_type = 'double precision'
            elif isinstance(test_value, basestring):
                cast_type = None
            else:
                raise ValueError('invalid value %r' % test_value)

            if cast_type:
                self.lvalue = "NULLIF(%%s->'%s', '')::%s" % (key, cast_type)
            else:
                self.lvalue = "%%s->'%s'" % key
        else:
            raise TypeError('invalid lookup type')

    def sql_for_column(self, qn, connection):
        if self.alias:
            return '%s.%s' % (qn(self.alias), qn(self.field))
        else:
            return qn(self.field)

    def as_sql(self, qn=None, connection=None):
        lvalue = self.lvalue % self.sql_for_column(qn, connection)
        expr = '%s %s %%s' % (lvalue, self.operator)
        return (expr, self.values)


class HQ(tree.Node):
    AND = 'AND'
    OR = 'OR'
    default = AND
    query_terms = VALUE_OPERATORS.keys()

    def __init__(self, **kwargs):
        super(HQ, self).__init__(children=kwargs.items())

    def _combine(self, other, conn):
        if not isinstance(other, HQ):
            raise TypeError(other)
        obj = type(self)()
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def add_to_query(self, query, used_aliases):
        self.add_to_node(query.where, query, used_aliases)

    def add_to_node(self, where_node, query=None, used_aliases=None):
        for child in self.children:
            if isinstance(child, HQ):
                node = query.where_class()
                child.add_to_node(node, query, used_aliases)
                where_node.add(node, self.connector)
            else:
                field, value = child
                parts = field.split(LOOKUP_SEP)
                if not parts:
                    raise FieldError("Cannot parse keyword query %r" % field)
                lookup_type = self.query_terms[0]  # Default lookup type
                num_parts = len(parts)
                if len(parts) > 1 and parts[-1] in self.query_terms:
                    # Traverse the lookup query to distinguish related fields from
                    # lookup types.
                    lookup_model = query.model
                    for counter, field_name in enumerate(parts):
                        if field_name == '_dfields':
                            continue

                        try:
                            lookup_field = lookup_model._meta.get_field(field_name)
                        except FieldDoesNotExist:
                            # Not a field. Bail out.
                            lookup_type = parts.pop()
                            break
                        # Unless we're at the end of the list of lookups, let's attempt
                        # to continue traversing relations.
                        if parts[0] != '_dfields' and (counter + 1) < num_parts:
                            try:
                                lookup_model = lookup_field.rel.to
                            except AttributeError:
                                # Not a related field. Bail out.
                                lookup_type = parts.pop()
                                break

                if parts[0] != '_dfields' and lookup_type == 'contains':
                    key = None
                else:
                    key = parts[-1]
                    parts = parts[:-1]

                opts = query.get_meta()
                alias = query.get_initial_alias()
                field, target, opts, join_list, last, extra = query.setup_joins(parts, opts, alias, True)
                col, alias, join_list = query.trim_joins(
                    target, join_list, last, False, False)
                where_node.add(HStoreConstraint(
                    alias, col, value, lookup_type, key), self.connector)

        if self.negated:
            where_node.negate()


class FlattenFieldsFilterQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(FlattenFieldsFilterQuerySet, self).__init__(*args, **kwargs)
        self.all_dynamic_field_names = self.model._meta.get_all_dynamic_field_names()
        self.all_field_names = self.model._meta.get_all_field_names()
        

    def _update(self, values):
        def is_not_dynamic(value):
            return not value[0].db_type == 'dynamic_field'
        values = filter(is_not_dynamic, values)
        return super(FlattenFieldsFilterQuerySet, self)._update(values)

    def hstore_override_method(self, method, *args, **kwargs):
        from hstore_flattenfields.db.base import HStoreModel
        queries = []
        super_cls = super(FlattenFieldsFilterQuerySet, self)
        opts = self.model._meta
        
        for key in kwargs.keys():
            if key.split('__')[0] in self.all_dynamic_field_names:
                
                if isinstance(kwargs[key], int):
                    kwargs[key] = str(kwargs[key])

                queries.append(
                    Q(HQ(**{
                        "_dfields__%s" % key: kwargs[key]
                    }))
                )
            elif '__' in key and not key.split('__')[1] in VALUE_OPERATORS.keys():
                if isinstance(kwargs[key], int):
                    kwargs[key] = str(kwargs[key])

                if hasattr(opts.get_field_by_name(key.split('__')[0])[0], 'field') and\
                 opts.get_field_by_name(key.split('__')[0])[0].field.__class__.__name__ == 'ForeignKey' and \
                 issubclass(opts.get_field_by_name(key.split('__')[0])[0].model, HStoreModel) and \
                 key.split('__')[1] in opts.get_field_by_name(key.split('__')[0])[0].model._meta.get_all_dynamic_field_names():
                    recursive_key = "%s___dfields__%s" % tuple(key.split('__'))
                    queries.append(
                        Q(HQ(**{
                            recursive_key: kwargs[key]
                        }))
                    )
                elif opts.get_field_by_name(key.split('__')[0])[0].__class__.__name__ == 'ForeignKey' and \
                 issubclass(opts.get_field_by_name(key.split('__')[0])[0].model, HStoreModel) and \
                 key.split('__')[1] in opts.get_field_by_name(key.split('__')[0])[0].model._meta.get_all_dynamic_field_names():
                    recursive_key = "%s___dfields__%s" % tuple(key.split('__'))
                    queries.append(
                        Q(HQ(**{
                            recursive_key: kwargs[key]
                        }))
                    )
            else:
                queries.append(Q(**{key: kwargs[key]}))
        try:
            super_method = getattr(super_cls, method)
            return super_method(*queries)
        except:
            return self.model.objects.none()

    def quote_name(self, name):
        return '"%s"' % name

    def values(self, *fields):
        if not fields:
            fields = self.all_field_names
        
        return parse_queryset(
            self.model,
            super(FlattenFieldsFilterQuerySet, self).values(*fields)
        )

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        query = self.query.clone()
        if self._sticky_filter:
            query.filter_is_sticky = True
        c = klass(model=self.model, query=query, using=self._db)
        c._for_write = self._for_write
        c._prefetch_related_lookups = self._prefetch_related_lookups[:]
        c.__dict__.update(kwargs)
        if setup and hasattr(c, '_setup_query'):
            c._setup_query()
        return c

    def values_list(self, *fields, **kwargs):
        if not fields and not kwargs.get('flat', False):
            # FIXME: Actually, the values_list
            # doesnt is flattening the data inside hstore.
            fields = self.all_field_names
        return super(FlattenFieldsFilterQuerySet, self).values_list(
            *fields, **kwargs
        )

    def filter(self, *args, **kwargs):
        return self.hstore_override_method(
            'filter', *args, **kwargs
        )

    def exclude(self, *args, **kwargs):
        return self.hstore_override_method(
            'exclude', *args, **kwargs
        )

    def where(self, *args):
        clone = self._clone()
        statement = AND(*args)

        _sql, _params = statement.as_sql(self.quote_name, clone)
        if hasattr(_sql, 'to_str'):
            _sql = _sql.to_str()

        clone.query.where.add(ExtraWhere([_sql], _params), "AND")
        return clone
