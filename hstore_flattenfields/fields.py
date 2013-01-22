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

import models as hs_models
import widgets as hs_widgets

FIELD_TYPES = ['Input', 'Monetary', 'Float', 'Integer', 'TextArea',
    'SelectBox', 'MultSelect', 'Date', 'DateTime', 'CheckBox', 'RadioButton']

FIELD_TYPES_WITHOUT_BLANK_OPTION = ['MultSelect', 'CheckBox', 'RadioButton']

FIELD_TYPES_DICT = dict(Input='models.CharField',
    Monetary='models.DecimalField',
    Float='models.FloatField',
    Integer='models.IntegerField',
    TextArea='models.TextField',
    SelectBox='UncleanedCharField',
    MultSelect='MultiSelectField',
    Date='models.CharField',
    DateTime='models.CharField',
    CheckBox='MultiSelectField',
    RadioButton='UncleanedCharField')

FIELD_TYPE_DEFAULT = 'models.CharField'


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

        # FIXME: this maybe mistake with fields with same name in different refers
        # dynamic_field = hs_models.DynamicField.objects.get(name=self.name)
        dynamic_field = hs_models.find_dfields(refer='Contact', name=self.name)[0]


        if dynamic_field.has_blank_option:
            choices = super(UncleanedCharField, self).get_choices()

        return choices or self._choices



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
                defaults['empty_value'] = None

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
