#!/usr/bin/env python
# encoding: utf-8
u"""
admin.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2011 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.contrib import admin

from hstore_flattenfields.models import *

def register(Model):
    """
    >>> from hstore_flattenfields.models import DynamicField 
    >>> register(DynamicField)
    >>> register(DynamicField)
    """
    try:
        admin.site.register(Model)
    except admin.sites.AlreadyRegistered:  
        pass

map(register, [DynamicFieldGroup, ContentPane, DynamicField])