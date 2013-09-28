#!/usr/bin/env python
# encoding: utf-8
"""
fields.py

Created by Luan Fonseca de Farias on 2013-09-23.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms

from .widgets import SelectMultipleWidget


class HstoreTextFieldFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.Textarea(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreTextFieldFormField, self).__init__(*args, **kwargs)


class HstoreNumberFormField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.TextInput(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreNumberFormField, self).__init__(*args, **kwargs)


class HstoreCharFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.TextInput(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreCharFormField, self).__init__(*args, **kwargs)


class HstoreDecimalFormField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.TextInput(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreDecimalFormField, self).__init__(*args, **kwargs)


class HstoreDateFormField(forms.DateField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.DateInput(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreDateFormField, self).__init__(*args, **kwargs)


class HstoreDateTimeFormField(forms.DateField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.DateTimeInput(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreDateTimeFormField, self).__init__(*args, **kwargs)


class RadioSelectField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.RadioSelect(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(RadioSelectField, self).__init__(*args, **kwargs)


class HstoreCheckboxInput(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.widget = forms.CheckboxSelectMultiple(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(HstoreCheckboxInput, self).__init__(*args, **kwargs)


class MultipleSelectField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.widget = SelectMultipleWidget(
            attrs=kwargs.pop('html_attrs', {})
        )
        super(MultipleSelectField, self).__init__(*args, **kwargs)
