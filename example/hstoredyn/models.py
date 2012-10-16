'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from django import forms

from django_orm.postgresql import hstore
from django.utils.datastructures import SortedDict
import copy
from django.forms.models import fields_for_model
from hstore_flattenfields.models import *


class Something(HStoreModel):
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name

class SomethingForm(HStoreModelForm):
    class Meta:
        model = Something


