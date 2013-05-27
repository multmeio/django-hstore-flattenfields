#!/usr/bin/env python
# encoding: utf-8

import re
from django import template

register = template.Library()

@register.filter
def get_attr(instance, arg):
    numeric_test = re.compile("^\d+$")
    # TODO: Pass to settings.py
    pretty_arg = 'pretty_' + str(arg)
    result = ''

    if hasattr(instance, pretty_arg):
        result = getattr(instance, pretty_arg)
    elif hasattr(instance, str(arg)):
        result = getattr(instance, arg)
    elif hasattr(instance, 'has_key') and instance.has_key(arg):
        # Dict
        result = instance[arg]
    elif numeric_test.match(str(arg)) and len(instance) > int(arg):
        # Lists
        result = instance[int(arg)]

    if result.__class__.__name__ == "ManyRelatedManager":
        result = ", ".join([
            unicode(m2m) for m2m in result.all()
        ]) + "."

    return result
