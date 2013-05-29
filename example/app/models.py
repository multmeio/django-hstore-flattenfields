'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from hstore_flattenfields.models import HStoreModel

import utils

class Something(HStoreModel):
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

    @property
    def fields_template(self):
        excludes = ['_dfields']
        return utils._unpack_fields(self, excludes)
