#!/usr/bin/env python
# encoding: utf-8
"""
widgets.py

Created by Luan Fonseca on 2013-01-21.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms
from django.utils.safestring import mark_safe

from utils import str2literal

class SelectMultipleWidget(forms.SelectMultiple):
    def render(self, name, value='', attrs={}, choices=()):
        html = super(SelectMultipleWidget, self).render(
            name, str2literal(value), attrs, choices)
        return mark_safe(html)


class RealCurrencyInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        value = value or ''
        attrs = attrs or {}

        if isinstance(value, Decimal):
            value = floatformat(str(value), 2)

        html = super(RealCurrencyInput, self).render(name, value, attrs)
        return mark_safe(html)
