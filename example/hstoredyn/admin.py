'''
Created on 13/10/2012

@author: iuri
'''
from hstore_flattenfields.models import DynamicField
from django.contrib import admin

from hstoredyn.models import Something

admin.site.register(Something)
admin.site.register(DynamicField)
