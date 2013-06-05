#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2011 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms
from django.forms.models import fields_for_model
from django.db.models import SubfieldBase

import models as hs_models
import widgets as hs_widgets

class HStoreModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HStoreModelForm, self).__init__(*args, **kwargs)
        # Always override for fields (dynamic fields maybe deleted/included)
        opts = self._meta
        if opts.model and issubclass(opts.model, hs_models.HStoreModel):
            # If a model is defined, extract dynamic form fields from it.
            if not opts.exclude:
                opts.exclude = []
            # hide dfields
            opts.exclude.append('_dfields')
            self.fields = fields_for_model(opts.model, opts.fields,
                                              opts.exclude, opts.widgets)


class MultipleSelectFieldWidgetHandler(forms.TypedMultipleChoiceField):
    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        self.widget = hs_widgets.SelectMultipleWidget
        super(MultipleSelectFieldWidgetHandler, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value
