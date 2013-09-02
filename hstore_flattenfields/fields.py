#!/usr/bin/env python
# encoding: utf-8
"""
fields.py

Created by Luan Fonseca on 2013-01-21.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms
from django.db import models
from django.utils.text import capfirst
from decimal import Decimal, InvalidOperation
from datetime import date, datetime

import models as hs_models
import widgets as hs_widgets
import forms as hs_forms
from utils import *


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
    CheckBox='HstoreMultipleSelectField',
    RadioButton='HstoreCharField'
)
FIELD_TYPES = FIELD_TYPES_DICT.keys()

class HstoreTextField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreTextField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is models.fields.NOT_PROVIDED:
            return ''
        else:
            return super(HstoreTextField, self).to_python(value)


class HstoreFloatField(models.FloatField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreFloatField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            return None

        if isinstance(value, float):
            return value
        else:
            return float(value)


class HstoreIntegerField(models.IntegerField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreIntegerField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            return None

        if isinstance(value, int):
            return value
        else:
            try:
                return int(value)
            except ValueError:
                return None

    def _get_val_from_obj(self, obj):
        try:
            return getattr(obj, self.attname)
        except AttributeError:
            return getattr(obj, self.name)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if value:
            return int(value)

    def clean(self, value, *args):
        return value


class HstoreCharField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def clean(self, value, *args):
        return unicode(value)

    def get_choices(self, include_blank=False):
        choices = []

        # FIXME: this maybe mistake on fields with same name in different refers
        try:
            dynamic_field = hs_models.find_dfields(name=self.name)[0]
            if dynamic_field.has_blank_option:
                choices = super(HstoreMultipleSelectField, self).get_choices()
        except IndexError:
            pass

        return choices or self._choices

    def to_python(self, value):
        if value is models.fields.NOT_PROVIDED:
            return ''

        return value


class HstoreDecimalField(models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreDecimalField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        if value is models.fields.NOT_PROVIDED:
            return None

        try:
            value = Decimal(value)
            return value
        except InvalidOperation:
            return ''

    def clean(self, value, *args):
        return unicode(value)


class HstoreDateField(models.DateField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreDateField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED or value == 'None':
            return None
        return str2date(value)

    def clean(self, value, *args):
        if value == 'None' or not value:
            return ''
        return value

    def _get_val_from_obj(self, obj):
        try:
            return getattr(obj, self.attname)
        except AttributeError:
            return getattr(obj, self.name)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)

        if value and isinstance(value, date):
            return value.isoformat()
        return ''

class HstoreDateTimeField(models.DateTimeField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreDateTimeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED or value == 'None':
            return None
        return str2datetime(value)

    def clean(self, value, *args):
        if value == 'None' or not value:
            return ''
        return value

    def _get_val_from_obj(self, obj):
        try:
            return getattr(obj, self.attname)
        except AttributeError:
            return getattr(obj, self.name)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)

        if value and isinstance(value, datetime):
            return value.isoformat()
        return ''


class HstoreSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(HstoreSelectField, self).__init__(*args, **kwargs)

    def clean(self, value, *args):
        #FIXME: At the beginning of the project there was
        #       a bug that was saving the value as a string: 'None'
        if value == 'None' or not value: return ''
        return value

    def to_python(self, value):
        if value is models.fields.NOT_PROVIDED:
            return ''
        return value


class HstoreMultipleSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def clean(self, value, *args, **kwargs):
        return value

    # XXX: Override formfield
    # most code was copied from django 1.4.1: db.models.CharField.formfield)
    # only changed TypedChoiceField to MultipleChoiceField
    def formfield(self, form_class=hs_forms.MultipleSelectFieldWidgetHandler, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text
        }

        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or \
                            not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = ""

            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that TypedChoiceField will understand.
            for k in kwargs.keys():
                if k not in ('coerce', 'empty_value', 'choices', 'required',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is models.fields.NOT_PROVIDED:
            return []
        return str2literal(value)

    def get_choices(self, include_blank=False):
        choices = []

        # FIXME: this maybe mistake on fields with same name in different refers
        try:
            dynamic_field = hs_models.find_dfields(name=self.name)[0]
            if dynamic_field.has_blank_option:
                choices = super(HstoreMultipleSelectField, self).get_choices()
        except IndexError:
            pass

        return choices or self._choices


def create_choices(choices=''):
    if not choices: choices = ''

    return single_list_to_tuple([
        s.strip() for s in choices.splitlines()
    ])

def get_modelfield(typo):
    return eval(
        FIELD_TYPES_DICT.get(
            typo, FIELD_TYPE_DEFAULT
        )
    )

def crate_field_from_instance(instance):
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
        help_text='',
        # XXX: HARDCODED "_dfields"
        db_column="_dfields->'%s'" % instance.name,
    )

    field.db_type = 'dynamic_field'
    field.attname = field.name
    field.column = field.db_column

    instance.get_modelfield = field
    return field
