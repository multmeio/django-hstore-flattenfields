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

def get_dynamic_from_cache(name):
    return [f for f in cache.get('dynamic_fields') \
            if f.name == name][0]


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
        if value is models.fields.NOT_PROVIDED:
            return ''
        else:
            return super(HstoreTextField, self).to_python(value)


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

    def clean(self, value, *args):
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

    def clean(self, value, *args):
        return unicode(value)

    def get_choices(self, include_blank=False):
        choices = []

        # FIXME: this maybe mistake on fields with same name in different
        # refers
        try:
            dynamic_field = get_dynamic_from_cache(self.name)
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

    def clean(self, value, *args):
        if not value:
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

    def clean(self, value, *args):
        if not value:
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
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreSelectField, self).__init__(*args, **kwargs)

    def clean(self, value, *args):
        # FIXME: At the beginning of the project there was
        #       a bug that was saving the value as a string: 'None'
        if not value:
            return ''
        return value

    def to_python(self, value):
        if value is models.fields.NOT_PROVIDED:
            return ''
        return value


class HstoreRadioSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreRadioSelectField, self).__init__(*args, **kwargs)

    # XXX: Override formfield
    # most code was copied from django 1.4.1: db.models.CharField.formfield)
    # only changed TypedChoiceField to MultipleChoiceField
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
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
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
        if value is models.fields.NOT_PROVIDED or value is None:
            return None
        else:
            return value

    def get_choices(self, include_blank=False):
        choices = []

        # FIXME: this maybe mistake on fields with same name in different
        # refers
        try:
            dynamic_field = get_dynamic_from_cache(self.name)
            if dynamic_field.has_blank_option:
                choices = super(HstoreRadioSelectField, self).get_choices()
        except IndexError:
            pass
        return choices or self._choices

    def get_default(self):
        return self.default


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
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
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
        formfield = form_class(**defaults)

        if self.html_attrs:
            formfield.widget.build_attrs(self.html_attrs)

        return formfield

    def clean(self, value, *args):
        return value

    def get_choices(self, include_blank=False):
        choices = []

        # FIXME: this maybe mistake on fields with same name in different
        # refers
        try:
            dynamic_field = get_dynamic_from_cache(self.name)
            if dynamic_field.has_blank_option:
                choices = super(HstoreCheckboxField, self).get_choices()
        except IndexError:
            pass
        return choices or self._choices

    def get_default(self):
        return self.default

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is models.fields.NOT_PROVIDED or value is None:
            return []
        return str2literal(value) or value


class HstoreMultipleSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.html_attrs = kwargs.pop('html_attrs', None)
        super(HstoreMultipleSelectField, self).__init__(*args, **kwargs)

    def clean(self, value, *args, **kwargs):
        return value

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
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
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

        # FIXME: this maybe mistake on fields with same name in different
        # refers
        try:
            dynamic_field = get_dynamic_from_cache(self.name)
            if dynamic_field.has_blank_option:
                choices = super(HstoreMultipleSelectField, self).get_choices()
        except IndexError:
            pass

        return choices or self._choices
