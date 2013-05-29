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

import models as hs_models
import widgets as hs_widgets
from utils import *

FIELD_TYPES = ['Input', 'Monetary', 'Float', 'Integer', 'TextArea',
    'SelectBox', 'MultSelect', 'Date', 'DateTime', 'CheckBox', 'RadioButton']

PRETTY_FIELDS = ["Monetary", "CheckBox", "MultSelect", "Date"]

FIELD_TYPES_WITHOUT_BLANK_OPTION = ['MultSelect', 'CheckBox', 'RadioButton']

FIELD_TYPES_DICT = dict(Input='models.CharField',
    Monetary='HstoreDecimalField',
    Float='models.FloatField',
    Integer='models.IntegerField',
    TextArea='models.TextField',
    SelectBox='SelectField',
    MultSelect='MultiSelectField',
    Date='models.CharField',
    DateTime='models.CharField',
    CheckBox='MultiSelectField',
    RadioButton='UncleanedCharField')

FIELD_TYPE_DEFAULT = 'models.CharField'


class HstoreDecimalField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        super(HstoreDecimalField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """

        try:
            value = Decimal(value)
            return value
        except InvalidOperation:
            # FIXME: In the case of the form send a u'None' in value
            super(HstoreDecimalField, self).to_python(str2literal(value))


class MultipleSelectField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.widget = hs_widgets.SelectMultipleWidget
        super(MultipleSelectField, self).__init__(*args, **kwargs)


class UncleanedCharField(models.CharField):
    def clean(self, value, *args):
        # ignore clean
        return value

    def get_choices(self, include_blank=False):
        """
        Overriding the method to remove the
        BLANK_OPTION in Checkbox, Radio and Select.

        * Only if the dfield is blank
        """
        choices = []

        # FIXME: this maybe mistake on fields with same name in different refers
        try:
            dynamic_field = hs_models.find_dfields(name=self.name)[0]
            if dynamic_field.has_blank_option:
                choices = super(UncleanedCharField, self).get_choices()
        except IndexError:
            pass

        return choices or self._choices


class SelectField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(SelectField, self).__init__(*args, **kwargs)

    def clean(self, value, *args):
        #FIXME: At the beginning of the project there was
        #       a bug that was saving the value as a string: 'None'
        if value == 'None' or not value: return ''
        return value


class MultiSelectField(UncleanedCharField):
    # XXX: Override formfield
    # most code was copied from django 1.4.1: db.models.CharField.formfield)
    # only changed TypedChoiceField to MultipleChoiceField
    def formfield(self, form_class=forms.CharField, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text}
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

            form_class = MultipleSelectField
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


def create_choices(choices=''):
    if not choices: choices = ''

    return single_list_to_tuple([
        s.strip() for s in choices.splitlines()
    ])

def crate_field_from_instance(instance):
    class_name = FIELD_TYPES_DICT.get(
        instance.typo, FIELD_TYPE_DEFAULT
    )

    FieldClass = eval(class_name)

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

    return field
