'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from django import forms

from django_orm.postgresql import hstore

class DynamicFields(models.Model):
    refer = models.CharField(max_length=120, blank=False)
    name = models.CharField(max_length=120, blank=False)
    type = models.CharField(max_length=120, blank=False)
    max_length = models.IntegerField(null=True, blank=True)
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    required = models.BooleanField(default=True)
    choices = hstore.DictionaryField(null=True)

    objects = hstore.HStoreManager()


class MyModelMeta(models.Model.__metaclass__):
    def __new__(cls, name, bases, attrs):
        super_new = super(MyModelMeta, cls).__new__

        # create it
        new_class = super_new(cls, name, bases, attrs)

        # pos create

        # override getattr/setattr/delattr
        def __getattr__(self, key):
            if not key in self._dfields:
                raise AttributeError("no such key %s" % key)
            return self._dfields[key]
        new_class.__getattr__ = __getattr__

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            if hasattr(self, '_dfields') and not key in dir(new_class):
                # XXX: search for key on table, django will call this method on many times on 
                #      __init__
                if DynamicFields.objects.filter(refer=new_class.__name__, name=key):
                    self._dfields[key] = value
                    return

            old_setattr(self, key, value)

        new_class.__setattr__ = __setattr__

        old_delattr = new_class.__delattr__
        def __delattr__(self, key):
            if hasattr(self, '_dfields') and not key in dir(new_class):
                if key in self._dfields:
                    del self._dfields[key]
                    return

            return old_delattr(self, key)
        new_class.__delattr__ = __delattr__

        # return it
        return new_class

class MyModel(models.Model):
    __metaclass__ = MyModelMeta
    objects = hstore.HStoreManager()
    _dfields = hstore.DictionaryField(db_index=True)
    class Meta:
        abstract = True

#######################################################

class Something(MyModel):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(db_index=True)

    def __unicode__(self):
        return self.name

class SomethingForm(forms.ModelForm):
    class Meta:
        model = Something


