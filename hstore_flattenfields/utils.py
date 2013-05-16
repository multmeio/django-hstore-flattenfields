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

__all__ = ['single_list_to_tuple',
           'str2literal',
           'dec2real',
           'has_any_in',
           'DYNAMIC_FIELD_TABLE_EXISTS'
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

def has_any_in(chances, possibilities):
    return any([x for x in chances if x in possibilities])

def DYNAMIC_FIELD_TABLE_EXISTS():
    # NOTE: Error happen on syncdb, because DynamicField's table does not exist.
    cursor = connection.cursor()
    cursor.execute("select count(*) from pg_tables where tablename='dynamic_field'")
    return cursor.fetchone()[0] > 0
