'''
Created on 24/05/2013

@author: luan
'''

from hstore_flattenfields.forms import HStoreModelForm

from models import Something

class SomethingForm(HStoreModelForm):
    class Meta:
        model = Something
