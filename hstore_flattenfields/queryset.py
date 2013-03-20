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

parse_column_type = {
    "IntegerField": """CAST(NULLIF({0}, '') AS integer)""",
    "HstoreDecimalField": """CAST(NULLIF({0}, '') AS float)""",
}

where_filters = {
    u"exact": """{0} = %s""",

    u"gt": """{0} > %s""",
    u"gte": """{0} >= %s""",
    u"lt": """{0} < %s""",
    u"lte": """{0} <= %s""",
    u"range": """{0} BETWEEN %s AND %s""",

    u"iexact": """UPPER({0}) = UPPER(%s)""",
    u"contains": """{0} LIKE %s""",
    u"icontains": """{0} ILIKE %s""",
    u"startswith": """{0} LIKE %s""",
    u"istartswith": """{0} ILIKE %s""",
    u"endswith": """{0} LIKE %s""",
    u"iendswith": """{0} ILIKE %s""",

    # u"range_dates": """{0} BETWEEN %s AND %s""",

    u"isnull": """{0} = %s""",
}

value_filters = {
    u"exact": """{0}""",

    u"gt": """{0}""",
    u"gte": """{0}""",
    u"lt": """{0}""",
    u"lte": """{0}""",

    u"iexact": """{0}""",
    u"contains": """%{0}%""",
    u"icontains": """%{0}%""",
    u"startswith": """{0}%""",
    u"istartswith": """{0}%""",
    u"endswith": """%{0}""",
    u"iendswith": """%{0}%""",

    # u"range_dates": """CAST(%s::date AS varchar) AND CAST(%s::interval AS varchar)""",

    u"isnull": """''""",
}

class FlattenFieldsFilterQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(FlattenFieldsFilterQuerySet, self).__init__(*args, **kwargs)
        self.all_field_names = self.model._meta.get_all_field_names()

    def parse_column(self, field):
        try:
            db_column = parse_column_type[field.__class__.__name__].format(
                field.db_column
            )
        except KeyError:
            db_column = field.db_column

        return db_column

    def values(self, *fields):
        if not fields:
            fields = self.all_field_names

        result = []
        for obj in super(FlattenFieldsFilterQuerySet, self)._clone():
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
        for obj in super(FlattenFieldsFilterQuerySet, self)._clone():
            _list = []
            for field in fields:
                _list.append(
                    getattr(obj, field, None)
                )
            result.append(tuple(_list))
        return result

    def filter(self, *args, **kwargs):
        where_conditions = []
        value_conditions = []
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
                if filter_type == "in":
                    import ipdb; ipdb.set_trace()


                if type(value) != list:
                    # FIXME: We have to send strings
                    # to hstore, and inside the sql query
                    # we made the cast.
                    value = [unicode(value)]

                where_conditions.append(
                    where_filters[filter_type].format(
                        self.parse_column(field)
                    )
                )

                try:
                    value_conditions.append(
                        value_filters[filter_type].format(
                            *value
                        )
                    )
                except KeyError:
                    if filter_type == "range":
                        value_conditions = tuple(value)
                    else:
                        value_conditions = value

        return self.extra(
            where=where_conditions,
            params=value_conditions
        )


class FlattenFieldsFilterManager(hstore.HStoreManager):
    def get_query_set(self):
        return FlattenFieldsFilterQuerySet(self.model)

