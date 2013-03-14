#!/usr/bin/env python
# encoding: utf-8
"""
manager.py

Created by Luan Fonseca de Faroas on 2013-03-13.
Copyright (c) 2013 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.db.models.fields import FieldDoesNotExist
from django_orm.postgresql import hstore
from django.db.models.query import *

from utils import *

query_map_filters = {
    u"exact": """{0} = '{1}'""",
    u"iexact": """{0} = LOWER('{1}')""",
    u"contains": """{0} LIKE '%{1}%'""",
    u"icontains": """{0} ILIKE '%{1}%'""",
    # "in": """  """,
    u"gt": """{0} > '{1}'""",
    u"gte": """{0} >= '{1}'""",
    u"lt": """{0} < '{1}'""",
    u"lte": """{0} <= '{1}'""",
    u"startswith": """{0} LIKE '%{1}'""",
    u"istartswith": """{0} ILIKE '%{1}'""",
    u"endswith": """{0} LIKE '{1}'%""",
    u"iendswith": """{0} ILIKE '{1}'%""",
    u"range": """{0} BETWEEN '{1}' AND '{2}'""",
    u"range_dates": """{0} BETWEEN CAST('{1}'::date AS varchar) AND CAST('{2}'::interval AS varchar)""",
    u"isnull": """{0} = ''""",
}

query_sql = u"""SELECT %(fields)s FROM %(table)s WHERE %(condition)s"""

class FlattenFieldsFilterQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(FlattenFieldsFilterQuerySet, self).__init__(*args, **kwargs)
        self.all_field_names = self.model._meta.get_all_field_names()

    def values(self, *fields):
        if not fields:
            fields = self.all_field_names

        result = []
        for obj in super(FlattenFieldsFilterQuerySet, self).filter():
            _dict = {}
            for field in fields:
                _dict.update({
                    field: getattr(obj, field, None)
                })
            result.append(_dict)
        return result

    def values_list(self, *fields, **kwargs):
        if not fields:
            fields = self.all_field_names

        result = []
        for obj in super(FlattenFieldsFilterQuerySet, self).filter():
            _list = []
            for field in fields:
                _list.append(
                    getattr(obj, field, None)
                )
            result.append(tuple(_list))
        return result

    def filter(self, *args, **kwargs):
        query_table = self.model._meta.db_table

        # FIXME: If his father inherits from hstore
        #        i.e.: Customer <- Organization and Person
        parent_classnames = [b.__base__.__name__ for b in self.model.__bases__]
        if has_any_in(parent_classnames, ['Customer']):
            query_table = self.model.__base__._meta.db_table

        query_conditions = []
        for orm_query_filter, value in kwargs.iteritems():
            try:
                field_name, filter_type = orm_query_filter.rsplit('__')
            except ValueError:
                field_name, filter_type = orm_query_filter, 'exact'

            try:
                field = self.model._meta.get_field_by_name(field_name)[0]
            except FieldDoesNotExist:
                # When is not a query in dfields... when is just a normal query
                return super(FlattenFieldsFilterQuerySet, self).filter(*args, **kwargs)
            else:
                query_condition = unicode(query_map_filters[filter_type]).format(
                    field.db_column, value
                )

            query_conditions.append(query_condition)
        return self.extra(where=query_conditions)


class FlattenFieldsFilterManager(hstore.HStoreManager):
    def get_query_set(self):
        return FlattenFieldsFilterQuerySet(self.model)

