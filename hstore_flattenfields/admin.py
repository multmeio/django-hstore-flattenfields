#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2011 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.contrib import admin

from .models import *

for Model in [DynamicFieldGroup, ContentPane, DynamicField]:
    try:
        admin.site.register(Model)
    except: 
        pass
