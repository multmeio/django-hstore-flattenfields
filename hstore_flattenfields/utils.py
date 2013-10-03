#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.template.defaultfilters import slugify, floatformat
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db import connection
from django.db.models import get_model
from django.conf import settings
from ast import literal_eval
from datetime import datetime, date
import re
import six


DATETIME_ISO_RE = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})$'
)
DATETIME_ISO_MS_RE = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}).(?P<microsecond>\d{1,6})$'
)
DATETIME_BR_RE = re.compile(
    r'(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})$'
)
DATETIME_BR_MS_RE = re.compile(
    r'(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}).(?P<microsecond>\d{1,6})$'
)
DATE_ISO_RE = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)
DATE_BR_RE = re.compile(
    r'(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})$'
)

REGEX_DATETIMES = [DATETIME_ISO_RE, DATETIME_ISO_MS_RE, DATETIME_BR_RE,
                   DATETIME_BR_MS_RE]
REGEX_DATES = [DATE_ISO_RE, DATE_BR_RE]

FIELD_TYPES_WITHOUT_BLANK_OPTION = ['MultSelect', 'CheckBox', 'RadioButton']
FIELD_TYPE_DEFAULT = 'HstoreCharField'
FIELD_TYPES_DICT = dict(
    Input='HstoreCharField',
    Monetary='HstoreDecimalField',
    Float='HstoreFloatField',
    Integer='HstoreIntegerField',
    TextArea='HstoreTextField',
    SelectBox='HstoreSelectField',
    MultSelect='HstoreMultipleSelectField',
    Date='HstoreDateField',
    DateTime='HstoreDateTimeField',
    CheckBox='HstoreCheckboxField',
    RadioButton='HstoreRadioSelectField'
)
FIELD_TYPES = FIELD_TYPES_DICT.keys()

SPECIAL_CHARS = [
    '_',
    '%',
    '\\',
]

SPECIAL_CHARS_OPERATORS = [
    'iexact',
    'contains',
    'icontains',
    'startswith',
    'istartswith',
    'endswith',
    'iendswith',
    'in',
]

VALUE_OPERATORS = {
    'exact': '=',
    'iexact': 'ILIKE',
    'contains': 'LIKE',
    'icontains': 'ILIKE',
    'startswith': 'LIKE',
    'istartswith': 'ILIKE',
    'endswith': 'LIKE',
    'iendswith': 'ILIKE',
    'regex': '~',
    'iregex': '~*',
    'in': 'IN',
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>=',
}

__all__ = ['single_list_to_tuple',
           'str2literal',
           'dec2real',
           'has_any_in',
           'dynamic_field_table_exists',
           'str2date',
           'str2datetime',
           'DATE_BR_RE',
           'get_fieldnames',
           'FIELD_TYPES_WITHOUT_BLANK_OPTION',
           'FIELD_TYPE_DEFAULT',
           'FIELD_TYPES_DICT',
           'FIELD_TYPES',
           'create_choices',
           'SPECIAL_CHARS',
           'SPECIAL_CHARS_OPERATORS',
           'VALUE_OPERATORS',
           'get_modelfield',
           'create_field_from_instance',
           'get_dynamic_field_model',
           'parse_queryset',
]


def single_list_to_tuple(list_values):
    return [(v, v) for v in list_values]


def str2literal(string):
    try:
        return literal_eval(string)
    except:
        return ''


def dec2real(value):
    return floatformat(value, 2)


def str2datetime(value):
    if isinstance(value, datetime):
        return value
    if not value:
        return ''

    for regex in REGEX_DATETIMES:
        match = regex.match(value)
        if match:
            break

    if match:
        kw = dict((k, int(v)) for k, v in six.iteritems(match.groupdict()))
        return datetime(**kw)
    raise ValidationError("Invalid datetime format for %s" % value)


def str2date(value):
    if isinstance(value, date):
        return value
    if not value:
        return ''

    for regex in REGEX_DATES:
        match = regex.match(value)
        if match:
            break

    if match:
        kw = dict((k, int(v)) for k, v in six.iteritems(match.groupdict()))
        return date(**kw)
    raise ValidationError("Invalid date format for %s" % value)


def has_any_in(chances, possibilities):
    return any([x for x in chances if x in possibilities])

# cache in globals
_DYNAMIC_FIELD_TABLE_EXISTS = None


def dynamic_field_table_exists():
    from hstore_flattenfields.models import DynamicField
    dynamic_field_table_name = DynamicField._meta.db_table
    global _DYNAMIC_FIELD_TABLE_EXISTS
    if not _DYNAMIC_FIELD_TABLE_EXISTS:
        _DYNAMIC_FIELD_TABLE_EXISTS = dynamic_field_table_name in connection.introspection.table_names()
    return _DYNAMIC_FIELD_TABLE_EXISTS


def get_fieldnames(fields, excludes=[]):
    return map(lambda f: f.name,
       filter(lambda f: f.name not in excludes, fields)
   )


def create_choices(choices=''):
    if not choices:
        choices = ''
    return single_list_to_tuple(
        map(lambda x: x.strip(), choices.splitlines())
    )


def get_modelfield(typo):
    from hstore_flattenfields.db import fields
    class_name = FIELD_TYPES_DICT.get(typo, FIELD_TYPE_DEFAULT)
    return getattr(fields, class_name)


def create_field_from_instance(instance):
    FieldClass = get_modelfield(instance.typo)

    # FIXME: The Data were saved in a string: "None"
    default_value = instance.default_value
    if default_value is None:
        default_value = ""

    field = FieldClass(name=instance.name,
        verbose_name=instance.verbose_name,
        max_length=instance.max_length or 255,
        blank=instance.blank,
        null=True,
        default=default_value,
        choices=create_choices(instance.choices),
        help_text=instance.help_text,
        db_column="_dfields->'%s'" % instance.name,
        html_attrs=instance.html_attrs,
    )

    field.db_type = 'dynamic_field'
    field.attname = field.name
    field.column = field.db_column

    instance.get_modelfield = field
    return field

def get_dynamic_field_model():
    """
    Function created to return the DynamicField
    class, to handle the Circular Imports
    against the .py Files.
    """
    from hstore_flattenfields.models import DynamicField
    return DynamicField

def intersec(l1, l2):
    return filter(
        lambda item: item, 
        set(l1).intersection(l2)
    )

def parse_queryset(model, result):
    dfield_names = model._meta.get_all_dynamic_field_names()
    for res in result:
        for item in intersec(dfield_names, res.keys()):
            try:
                parsed_value = model._meta.\
                    get_field_by_name(item)[0].\
                        to_python(res.get(item))
            except: continue
            else:
                res.update({item:parsed_value})
    return result