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
from django.core.cache import cache
from decimal import Decimal, InvalidOperation
from datetime import date, datetime

from hstore_flattenfields.utils import *
from hstore_flattenfields.forms.fields import *
from hstore_flattenfields.models import DynamicField

class HstoreTextField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreTextField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreTextFieldFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            value = None
        elif not isinstance(value, basestring):
            value = str(value)
        return value


class HstoreFloatField(models.FloatField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreFloatField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreNumberFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

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
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreIntegerField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreNumberFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

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

    def clean(self, value, instance):
        return value


class HstoreCharField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreCharField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreCharFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def get_choices(self, include_blank=False):
        dynamic_field = DynamicField.objects.get(name=self.name)

        choices = single_list_to_tuple(
            str2literal(dynamic_field.choices)
        )
        
        if include_blank and choices and \
           dynamic_field.has_blank_option:
            choices.insert(0, ('', '----'))
        return choices or self._choices

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            value = None
        elif not isinstance(value, basestring):
            value = str(value)
        return value


class HstoreDecimalField(models.DecimalField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreDecimalField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreDecimalFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        if not value or value is models.fields.NOT_PROVIDED:
            value = None
        elif not isinstance(value, Decimal):
            try:
                value = Decimal(value)
            except InvalidOperation:
                value = None
        return value


class HstoreDateField(models.DateField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreDateField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreDateFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            return None
        return str2date(value)

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

    def clean(self, value, instance):
        return value


class HstoreDateTimeField(models.DateTimeField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreDateTimeField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=HstoreDateTimeFormField, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            return None
        return str2datetime(value)

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

    def clean(self, value, instance):
        return value


class HstoreSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreSelectField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            value = None
        return value
    
    def get_choices(self, include_blank=False):
        dynamic_field = DynamicField.objects.get(name=self.name)

        choices = str2literal(dynamic_field.choices)
        return choices or self._choices


class HstoreRadioSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreRadioSelectField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=RadioSelectField, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }

        if self.has_default():
            defaults['initial'] = self.default

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
                             not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = ""
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        if value is models.fields.NOT_PROVIDED or value is None:
            return None
        else:
            return value

    def get_choices(self, include_blank=False):
        dynamic_field = DynamicField.objects.get(name=self.name)
        choices = single_list_to_tuple(
            str2literal(dynamic_field.choices)
        )
        return choices or self._choices


class HstoreCheckboxField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreCheckboxField, self).__init__(*args, **kwargs)

    # XXX: Override formfield
    # most code was copied from django 1.4.1: db.models.CharField.formfield)
    # only changed TypedChoiceField to MultipleChoiceField
    def formfield(self, form_class=HstoreCheckboxInput, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs,
        }

        if self.has_default():
            defaults['initial'] = self.default

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
                             not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = ""

        defaults.update(kwargs)
        formfield = form_class(**defaults)

        if self.html_attrs:
            formfield.widget.build_attrs(self.html_attrs)

        return formfield

    def get_choices(self, include_blank=False):
        choices = []
        dynamic_field = DynamicField.objects.get(name=self.name)
        choices = single_list_to_tuple(
            str2literal(dynamic_field.choices)
        )
        return choices or self._choices

    def get_default(self):
        return self.default

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is models.fields.NOT_PROVIDED or value is None:
            return []
        return str2literal(value) or value

    def clean(self, value, instance):
        return value


class HstoreMultipleSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreMultipleSelectField, self).__init__(*args, **kwargs)

    # XXX: Override formfield
    # most code was copied from django 1.4.1: db.models.CharField.formfield)
    # only changed TypedChoiceField to MultipleChoiceField
    def formfield(self, form_class=MultipleSelectField, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'html_attrs': self.html_attrs
        }

        if self.has_default():
            defaults['initial'] = self.default

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
                             not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = ""
        defaults.update(kwargs)
        return form_class(**defaults)

    def to_python(self, value):
        if not value or value is models.fields.NOT_PROVIDED:
            value = []
        
        if isinstance(value, basestring):
            value = str2literal(value)
        elif not isinstance(value, list):
            value = []

        return value

    def get_choices(self, include_blank=False):
        dynamic_field = DynamicField.objects.get(name=self.name)
        choices = single_list_to_tuple(
            str2literal(dynamic_field.choices)
        )
        if include_blank and choices:
            choices.insert(0, ('', '----'))
        return choices or self._choices

    def clean(self, value, instance):
        return value
