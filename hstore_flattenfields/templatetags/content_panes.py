#!/usr/bin/env python
# encoding: utf-8

from django import template
from django.template import Context, loader

from hstore_flattenfields.forms import HStoreContentPaneModelForm

register = template.Library()


def generic_loader(form, context, template):
    if not isinstance(form, HStoreContentPaneModelForm):
        return ''
    return loader.get_template(template).render(Context(context))

@register.filter(name='as_tabs')
def as_tabs(form):
    """
    Shows the form fields grouped in tabs.
    """
    return generic_loader(
        form=form, 
        context={'form': form}, 
        template='hstore_flattenfields/form.html'
    )

@register.filter(name='render_form_without_tabs')
def render_form_without_tabs(form):
    """
    Shows only the form without any tab.
    """
    return generic_loader(
        form=form, 
        context={'form': form}, 
        template='hstore_flattenfields/form_without_tabs.html'
    )

@register.filter(name='render_form_tabs')
def render_form_tabs(form):
    """
    Shows only the tabs.
    """
    return generic_loader(
        form=form, 
        context={'form': form}, 
        template='hstore_flattenfields/form_tabs.html'
    )
