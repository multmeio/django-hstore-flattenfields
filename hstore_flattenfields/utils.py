#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.template.defaultfilters import slugify, floatformat
from django.db import connection
from ast import literal_eval
from datetime import datetime

__all__ = ['single_list_to_tuple',
           'str2literal',
           'dec2real',
           'has_any_in',
           'dynamic_field_table_exists',
           'str2date',
           'str2datetime',
]


def single_list_to_tuple(list_values):
    return [(v, v) for v in list_values]

def str2literal(string):
    try:
        return literal_eval(string)
    except:
        return ''

def dec2real(value):
    return floatformat(value, 2)

def str2datetime(value, format="%Y-%m-%d %H:%M:%S.%f"):
    try:
        return datetime.strptime(
            value, format
        )
    except:
        return ''

def str2date(value):
    try:
        return str2datetime(value, "%Y-%m-%d").date()
    except:
        return ''

def has_any_in(chances, possibilities):
    return any([x for x in chances if x in possibilities])

# cache in globals
_DYNAMIC_FIELD_TABLE_EXISTS = None
def dynamic_field_table_exists():
    global _DYNAMIC_FIELD_TABLE_EXISTS
    if _DYNAMIC_FIELD_TABLE_EXISTS == None:
        _DYNAMIC_FIELD_TABLE_EXISTS = 'dynamic_field' in connection.introspection.table_names()
    return _DYNAMIC_FIELD_TABLE_EXISTS
