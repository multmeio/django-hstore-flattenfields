#!/usr/bin/env python
# encoding: utf-8

from django import template
from django.template import Context, loader

from hstore_flattenfields.forms import HStoreContentPaneModelForm

register = template.Library()


@register.filter(name='as_tabs')
def as_tabs(form, template='hstore_flattenfields/form.html'):
    """
    Shows the form fields grouped in tabs.
    """
    if not isinstance(form, HStoreContentPaneModelForm):
        return ''

    context = Context({'form': form})

    return loader.get_template(template).render(context)
