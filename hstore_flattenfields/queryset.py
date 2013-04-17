import datetime
import numbers
from django.utils import tree
from django.core.exceptions import FieldError
from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models.fields import FieldDoesNotExist
from django_orm.postgresql import hstore
from django.db.models.sql.where import ExtraWhere
from django_orm.core.sql.tree import AND, OR
from django.db.models.query import *
import operator

from utils import *

class HStoreConstraint():
    value_operators = {
        'exact': '=',
        'iexact': 'ILIKE',
        'contains': 'LIKE',
        'icontains': 'ILIKE',
        'startswith': 'LIKE',
        'istartswith': 'ILIKE',
        'endswith': 'LIKE',
        'iendswith': 'ILIKE',
        'in': 'IN',
        'lt': '<',
        'lte': '<=',
        'gt': '>',
        'gte': '>=',
    }

    def __init__(self, alias, field, value, lookup_type, key=None):
        self.lvalue = '%s'
        self.alias = alias
        self.field = field
        self.values = [value]

        # if lookup_type == 'contains':
        #     if isinstance(value, basestring):
        #         self.operator = '?'
        #     elif isinstance(value, (list, tuple)):
        #         self.operator = '?&'
        #         self.values = [list(value)]
            # else:
            #     raise ValueError('invalid value %r' % value)

        if lookup_type in self.value_operators:
            self.operator = self.value_operators[lookup_type]

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
                self.lvalue = "CAST(NULLIF(%%s->'%s', '') AS %s)" % (key, cast_type)
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
    query_terms = [
        'exact',
        'iexact',
        'lt',
        'lte',
        'gt',
        'gte',
        'in',
        'contains',
        'icontains',
        'startswith',
        'istartswith',
        'endswith',
        'iendswith',
    ]

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
            if  isinstance(child, HQ):
                node = query.where_class()
                child.add_to_node(node, query, used_aliases)
                where_node.add(node, self.connector)
            else:
                field, value = child
                parts = field.split(LOOKUP_SEP)
                if not parts:
                    raise FieldError("Cannot parse keyword query %r" % field)
                lookup_type = self.query_terms[0] # Default lookup type
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
                col, alias, join_list = query.trim_joins(target, join_list, last, False, False)
                where_node.add(HStoreConstraint(alias, col, value, lookup_type, key), self.connector)

        if self.negated:
            where_node.negate()


class FlattenFieldsFilterQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super(FlattenFieldsFilterQuerySet, self).__init__(*args, **kwargs)
        self.all_dynamic_field_names = self.model._meta.get_all_dynamic_field_names()
        self.all_field_names = self.model._meta.get_all_field_names()

    def values(self, *fields):
        if not fields:
            fields = self.all_field_names
        return super(FlattenFieldsFilterQuerySet, self).values(*fields)

    def values_list(self, *fields, **kwargs):
        if not fields and not kwargs.get('flat', False):
            # FIXME: Actually, the values_list
            # doesnt is flattening the data inside hstore.
            fields = self.all_field_names
        return super(FlattenFieldsFilterQuerySet, self).values_list(
            *fields, **kwargs
        )

    def filter(self, *args, **kwargs):
        queries = []

        for key in kwargs.keys():
            if key.split('__')[0] in self.all_dynamic_field_names:
                queries.append(
                    Q(HQ(**{"_dfields__%s" % key: kwargs[key]}))
                )
            else:
                queries.append(Q(**{key: kwargs[key]}))

        try:
            return super(FlattenFieldsFilterQuerySet, self).filter(
                *queries
            )
        except:
            pass

        return self.model.objects.none()

    def quote_name(self, name):
        return '"%s"' % name

    def where(self, *args):
        clone = self._clone()
        statement = AND(*args)

        _sql, _params = statement.as_sql(self.quote_name, clone)
        if hasattr(_sql, 'to_str'):
            _sql = _sql.to_str()

        clone.query.where.add(ExtraWhere([_sql], _params), "AND")
        return clone

class FlattenFieldsFilterManager(hstore.HStoreManager):
    def get_query_set(self):
        return FlattenFieldsFilterQuerySet(model=self.model, using=self._db)

