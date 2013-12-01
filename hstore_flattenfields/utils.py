#!/usr/bin/env python
# encoding: utf-8

"""
hstore_flattenfields.utils
-------------

The Models file where places all the stored classes
used in hstore_flattenfields application.

:copyright: 2012, multmeio (http://www.multmeio.com.br)
:author: 2012, Luís Antônio Araújo Brito <iuridiniz@gmail.com>
:license: BSD, see LICENSE for more details.
"""

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db import connection
from django.db.models import get_model, Q
from django.contrib.contenttypes.models import ContentType
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
           # 'get_dynamic_field_model',
           'parse_queryset',
           'all_flattenfields_tables_is_created',
           'build_flattenfields_object',
           'get_ctype',
]


def single_list_to_tuple(list_values):
    """
    >>> single_list_to_tuple([1, 2, 3, 4])
    [(1, 1), (2, 2), (3, 3), (4, 4)]
    >>> single_list_to_tuple(['a', 'b', 'c', 'd'])
    [('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd')]
    """
    return [(v, v) for v in list_values]


def str2literal(string):
    """
    >>> str2literal("{'foo': 'bar'}")
    {'foo': 'bar'}
    >>> str2literal("")
    ''
    >>> str2literal(20)
    ''
    """
    try:
        return literal_eval(string)
    except:
        return ''


def str2datetime(value):
    """
    >>> str2datetime('2009-04-20 00:00:20')
    datetime.datetime(2009, 4, 20, 0, 0, 20)
    >>> str2datetime('10/04/2013 10:20:30')
    datetime.datetime(2013, 4, 10, 10, 20, 30)
    >>> from datetime import datetime
    >>> dt = datetime(2013, 5, 8, 20, 10, 30)
    >>> str2datetime(dt)
    datetime.datetime(2013, 5, 8, 20, 10, 30)
    >>> str2datetime(None)
    ''
    >>> str2datetime('')
    ''
    >>> str2datetime('20@04@2009')
    Traceback (most recent call last):
        ...
    ValidationError: [u'Invalid datetime format for 20@04@2009']
    """
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
    """
    >>> str2date('2009-04-20')
    datetime.date(2009, 4, 20)
    >>> str2date('10/04/2013')
    datetime.date(2013, 4, 10)
    >>> from datetime import date
    >>> dt = date(2013, 5, 8)
    >>> str2date(dt)
    datetime.date(2013, 5, 8)
    >>> str2date(None)
    ''
    >>> str2date('')
    ''
    >>> str2date('20@04@2009')
    Traceback (most recent call last):
        ...
    ValidationError: [u'Invalid date format for 20@04@2009']
    """
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
    """
    >>> has_any_in(range(5), range(3, 6))
    True
    >>> has_any_in(range(5), range(6, 10))
    False
    >>> has_any_in(range(5), range(5))
    True
    """
    return any([x for x in chances if x in possibilities])


def all_flattenfields_tables_is_created(Models):
    db_table_names = connection.introspection.table_names()
    flattenfields_tables = map(lambda x: x._meta.db_table, Models)
    return all([x in db_table_names for x in flattenfields_tables])

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
    """
    >>> from tests.app.models import Author
    >>> get_fieldnames(Author()._meta.fields)
    ['id', '_dfields']
    >>> from tests.app.models import Author
    >>> get_fieldnames(Author()._meta.fields, ['_dfields'])
    ['id']
    """
    return map(lambda f: f.name,
       filter(lambda f: f.name not in excludes, fields)
   )


def create_choices(choices=''):
    """
    >>> create_choices([])
    []
    >>> create_choices('choice_01\\nchoice_02')
    [('choice_01', 'choice_01'), ('choice_02', 'choice_02')]
    >>> create_choices('choice_04 \\n choice_04')
    [('choice_04', 'choice_04'), ('choice_04', 'choice_04')]
    """
    if not choices:
        choices = ''
    return single_list_to_tuple(
        map(lambda x: x.strip(), choices.splitlines())
    )


def get_modelfield(typo):
    """
    >>> get_modelfield('Input')
    <class 'hstore_flattenfields.db.fields.HstoreCharField'>
    >>> get_modelfield('Integer')
    <class 'hstore_flattenfields.db.fields.HstoreIntegerField'>
    >>> get_modelfield('Random')
    <class 'hstore_flattenfields.db.fields.HstoreCharField'>
    """
    from hstore_flattenfields.db import fields
    class_name = FIELD_TYPES_DICT.get(typo, FIELD_TYPE_DEFAULT)
    return getattr(fields, class_name)


def create_field_from_instance(instance):
    """
    >>> from hstore_flattenfields.models import DynamicField
    >>> df = DynamicField(refer="Author", typo="Input", name="author_name", verbose_name=u"Name")
    >>> create_field_from_instance(df)
    <hstore_flattenfields.db.fields.HstoreCharField: author_name>
    """
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

# def get_dynamic_field_model():
#     """
#     Function created to return the DynamicField
#     class, to handle the Circular Imports
#     against the .py Files.
#     """
#     from hstore_flattenfields.models import DynamicField
#     return DynamicField

def intersec(l1, l2):
    """
    >>> intersec(set(range(5)), set(range(2, 7)))
    [2, 3, 4]
    """
    return filter(
        lambda item: item,
        set(l1).intersection(l2)
    )

def parse_queryset(model, result):
    """
    >>> from hstore_flattenfields.models import DynamicField
    >>> from tests.app.models import Author
    >>> DynamicField.objects.create(refer="Author", name="age", verbose_name=u"Age", typo="Integer")
    <DynamicField: Age>
    >>> DynamicField.objects.create(refer="Author", name="birth_date", verbose_name=u"Birth Date", typo="Date")
    <DynamicField: Birth Date>
    >>> author = Author.objects.create(age=20, birth_date='24/05/1992')
    >>> parse_queryset(Author, Author.objects.filter(id=author.id).values('age'))
    [{'age': 20}]
    >>> parse_queryset(Author, Author.objects.filter(id=author.id).values('birth_date'))
    [{'birth_date': datetime.date(1992, 5, 24)}]
    """
    dfield_names = model._meta.get_all_dynamic_field_names()
    for res in result:
        for item in intersec(dfield_names, res.keys()):
            field = model._meta.get_field_by_name(item)[0]
            res.update({
                item: field.to_python(res.get(item))
            })
    return result

def get_ctype(model):
    """
    >>> from tests.app.models import Author
    >>> get_ctype(Author)
    <ContentType: author>
    >>> get_ctype(None)
    Traceback (most recent call last):
      ...
    AttributeError: 'NoneType' object has no attribute '_meta'
    """
    return ContentType.objects.get_for_model(model)

def build_flattenfields_object(obj):
    """
    >>> from hstore_flattenfields.models import DynamicField, ContentPane
    >>> from hstore_flattenfields.utils import get_ctype
    >>> from tests.app.models import Author
    >>> DynamicField.objects.all().delete()
    >>> DynamicField.objects.create(refer="Author", name="author_age", verbose_name=u"Age", typo="Integer")
    <DynamicField: Age>
    >>> DynamicField.objects.create(refer="Author", name="author_birth_date", verbose_name=u"Birth Date", typo="Date")
    <DynamicField: Birth Date>
    >>> ContentPane.objects.create(name='Main Info', content_type=get_ctype(Author))
    <ContentPane: Main Info>
    >>> author = Author.objects.create(author_age=20, author_birth_date='24/05/1992')
    >>> author._dynamic_fields
    [<DynamicField: Age>, <DynamicField: Birth Date>]
    >>> author._content_panes
    [<ContentPane: Main Info>]
    >>> DynamicField.objects.all().delete()
    """
    try:
        from hstore_flattenfields.models import (
            DynamicField, ContentPane
        )
        assert dynamic_field_table_exists()
    except (AssertionError, ImportError):
        content_panes = metafields = []
    else:
        metafields = DynamicField.objects.filter(
            refer=obj.__class__.__name__
        ).order_by('pk')
        content_panes = ContentPane.objects.filter(
            Q(content_type__model=obj.__class__.__name__.lower())
        )
    setattr(obj, '_dynamic_fields', filter(lambda x: x, metafields))
    setattr(obj, '_content_panes', filter(lambda x: x, content_panes))
    setattr(obj._meta, '_model_dynamic_fields', 
            map(create_field_from_instance, metafields))
    