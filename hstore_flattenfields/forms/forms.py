#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2011 Multmeio [design+tecnologia]. All rights reserved.
"""

from django import forms
from django.forms.models import fields_for_model
from django.conf import settings

class HStoreModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        from hstore_flattenfields.models import HStoreModel

        super(HStoreModelForm, self).__init__(*args, **kwargs)
        # Always override for fields (dynamic fields maybe deleted/included)
        opts = self._meta
        if opts.model and issubclass(opts.model, HStoreModel):
            # If a model is defined, extract dynamic form fields from it.
            if not opts.exclude:
                opts.exclude = []
            # hide dfields
            opts.exclude.append('_dfields')
            
            opts.exclude.extend([
                f.name for f in opts.model._meta.dynamic_fields \
                if f.name not in map(lambda x: x.name, 
                                     self.instance._dynamic_fields)
            ])

            self.fields = fields_for_model(
                opts.model, opts.fields,
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

        model_name = self.Meta.model.__name__
        dynamic_field_names = map(lambda x: x.name, self.instance.dynamic_fields)
        
        if not hstore_order:
            def by_name_not_in(fieldname):
                return fieldname not in dynamic_field_names
            hstore_order = filter(by_name_not_in, self.fields.keyOrder)

        for field in self.instance.dynamic_fields:
            if field.name in hstore_order:
                hstore_order.pop(hstore_order.index(field.name))
            hstore_order.insert(field.order or len(hstore_order), field.name)
        self.fields.keyOrder = hstore_order

    def filtred_fields(self, content_pane=None):
        """
        Function to returns only the fields of was joined into a ContentPane
        Used in the template_filter named 'as_tabs'.

        If doesnt had content_pane, we have to iterate over
        all dynamic_fields and return the name of those field
        what have association with content_panes.
        """
        fields = self.visible_fields()
        dynamic_fields = self.instance._dynamic_fields
        
        if content_pane:
            field_names = [f.name for f in dynamic_fields if f.content_pane == content_pane]
            return [f for f in fields if f.name in field_names]
        else:
            field_names = [f.name for f in dynamic_fields if f.content_pane]
            return [f for f in fields if f.name not in field_names]

    @property
    def content_panes(self):
        grouped_panes = [{
            'name': getattr(settings, 'DEFAULT_CONTENT_PANE_NAME', 'Main Information'),
            'slug': 'default',
            'pk': '',
            'model': self.Meta.model.__name__,
            'fields': self.filtred_fields()
        }]
        
        for content_pane in self.instance.content_panes:
            has_error = any([
                f for f in self.instance.dynamic_fields
                if f.name in self.errors.keys() and \
                f.content_pane == content_pane
            ])

            grouped_panes.append({
                'name': content_pane.name,
                'slug': content_pane.slug,
                'pk': content_pane.pk,
                'model': self.Meta.model.__name__,
                'order': content_pane.order,
                'fields': self.filtred_fields(content_pane),
                'has_error': has_error
            })
        return grouped_panes
