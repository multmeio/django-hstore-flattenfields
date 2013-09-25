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
import re, six


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

REGEX_DATETIMES = [DATETIME_ISO_RE, DATETIME_ISO_MS_RE, DATETIME_BR_RE, DATETIME_BR_MS_RE]
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
    if isinstance(value, datetime): return value
    if not value: return ''

    for regex in REGEX_DATETIMES:
        match = regex.match(value)
        if match: break

    if match:
        kw = dict((k, int(v)) for k, v in six.iteritems(match.groupdict()))
        return datetime(**kw)
    raise ValidationError("Invalid datetime format for %s" % value)

def str2date(value):
    if isinstance(value, date): return value
    if not value: return ''

    for regex in REGEX_DATES:
        match = regex.match(value)
        if match: break

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
    if not choices: choices = ''
    return single_list_to_tuple(
        map(lambda x: x.strip(), choices.splitlines())
    )
