'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models

from hstore_flattenfields.models import HStoreModel
from hstore_flattenfields.forms import HStoreModelForm


class Something(HStoreModel):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class SomethingForm(HStoreModelForm):
    class Meta:
        model = Something
