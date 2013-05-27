'''
Created on 13/10/2012

@author: iuri
'''
from hstore_flattenfields.models import DynamicField
from django.contrib import admin

from app.models import Something

admin.site.register(Something)
