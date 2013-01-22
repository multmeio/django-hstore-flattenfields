#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.template.defaultfilters import slugify
from ast import literal_eval

__all__ = ['single_list_to_tuple',
           'str2literal',]


def single_list_to_tuple(list_values):
    return [(v, v) for v in list_values]

def str2literal(string):
    try:
        return literal_eval(string)
    except:
        return ''
