#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2011 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms
from django.forms.models import fields_for_model
from django.template import Context, loader

import models as hs_models
import widgets as hs_widgets
# from utils import get_dynamic_field_model

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


class HStoreContentPaneModelForm(HStoreModelForm):
    """
    Class created to wrapper the older HStoreModelForm
    and adding the feture of create 'content panes' filled with
    dynamic fields.

    he had a dependency of a model class called ContentPane
    and a config variable in the class what will have the content_pane,
    called cpane_related_field, telling to our class what field is used
    to get the certain content_pane and her fields and for the form be
    rendered in the right way, you must use the method called as_tabs
    in the template.
    """

    def __init__(self, *args, **kwargs):
        hstore_order = kwargs.pop('keyOrder', None)
        super(HStoreContentPaneModelForm, self).__init__(*args, **kwargs)

        self._dyn_fields = self.instance.dynamic_fields
        opts = self._meta.model._meta
        dfield_names = []

        # FIXME: Adding Inherit fields
        parent_local_fields = self.instance.__class__.__base__._meta.local_fields
        all_fields = [f.name for f in opts.local_fields + \
                                      opts.many_to_many + \
                                      parent_local_fields]
        for field in self._dyn_fields:
            field_name = field.name
            if isinstance(field, hs_models.DynamicField):
                field_widget = field.get_modelfield.formfield().widget
            else:
                field_widget = field.widget

            dfield_names.append(field_name)
            all_fields.append(field_name)

            if field_name in self.fields and field_widget:
                self.fields[field_name].widget = field_widget
                self.fields[field_name].localize = True

        if not hstore_order:
            hstore_order = [x for x in self.fields.keyOrder if not x in dfield_names]

        for field in hs_models.DynamicField.objects.find_dfields(refer=self.instance.__class__.__name__):
            if field.name in hstore_order:
                hstore_order.pop(hstore_order.index(field.name))
            hstore_order.insert(field.order or len(hstore_order), field.name)

        self.fields.keyOrder = hstore_order

        for name in self.fields.keys():
            if name not in all_fields:
                self.fields.pop(name)

        try:
            content_panes = self.instance.content_panes

            grouped_panes = [{'name': u'Default',
                              'slug': 'default',
                              'pk': '',
                              'fields': self.filtred_fields()}]

            for content_pane in content_panes:
                has_error = any([
                    f for f in content_pane.fields \
                        if f.name in self.errors.keys()
                ])

                grouped_panes.append({'name': content_pane.name,
                                      'slug': content_pane.slug,
                                      'pk': content_pane.pk,
                                      'fields': self.filtred_fields(content_pane),
                                      'has_error': has_error})
            self.content_panes = grouped_panes
        except:
            pass

    def filtred_fields(self, content_pane=None):
        """
        Function to returns only the fields of was joined into a ContentPane
        Used in the template_filter named 'as_tabs'.

        If doesnt had content_pane, we have to iterate over
        all dynamic_fields and return the name of those field
        what have association with content_panes.
        """
        fields = self.visible_fields()

        if self.instance:
            if content_pane:
                field_names = [f.name for f in content_pane.fields]
                return [f for f in fields if f.name in field_names]
            else:
                field_names = [f.name for f in self._dyn_fields if f.content_pane]
                return [f for f in fields if f.name not in field_names]
