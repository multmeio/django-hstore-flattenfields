#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.template.defaultfilters import slugify

__all__ = ['generate_alias',
           'single_list_to_tuple']


def generate_alias(value):
    return slugify(value).replace('-', '_')

def single_list_to_tuple(list_values):
    return [(generate_alias(v), v.capitalize()) for v in list_values]
