from django.db import models
from django.conf import settings

__all__ = [
    'HstoreSum',
    'HstoreCount',
    'HstoreAvg',
    'HstoreMax',
    'HstoreMin',
]

base_sql_template = "%(function)s(NULLIF(%(field)s, '')::{0})"


class HstoreAggregate(models.Aggregate):
    """
    Class created to handle the Aggregate in DynamicFields
    Because they are stored in string formats, and we have
    to parse, before the match in the select
    """
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = self.sql_klass(col, source=source, is_summary=is_summary, **self.extra)
        aggregate.sql_template = aggregate.sql_template.format(
            'integer' if is_summary else 'double precision'
        )
        query.aggregates[alias] = aggregate


class HstoreSumSQL(models.sql.aggregates.Aggregate):
    sql_function = 'SUM'
    sql_template = base_sql_template


class HstoreSum(HstoreAggregate):
    name = 'Sum'
    sql_klass = HstoreSumSQL


class HstoreCountSQL(models.sql.aggregates.Aggregate):
    sql_function = 'COUNT'
    sql_template = base_sql_template


class HstoreCount(HstoreAggregate):
    name = 'Count'
    sql_klass = HstoreCountSQL


class HstoreAvgSQL(models.sql.aggregates.Aggregate):
    sql_function = 'AVG'
    sql_template = base_sql_template


class HstoreAvg(HstoreAggregate):
    name = 'Avg'
    sql_klass = HstoreAvgSQL


class HstoreMaxSQL(models.sql.aggregates.Aggregate):
    sql_function = 'MAX'
    sql_template = base_sql_template


class HstoreMax(HstoreAggregate):
    name = 'Max'
    sql_klass = HstoreMaxSQL


class HstoreMinSQL(models.sql.aggregates.Aggregate):
    sql_function = 'MIN'
    sql_template = base_sql_template


class HstoreMin(HstoreAggregate):
    name = 'Min'
    sql_klass = HstoreMinSQL
