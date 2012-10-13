'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from django import forms

from django_orm.postgresql import hstore

class Something(models.Model):
    name = models.CharField(max_length=32)
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()

    def __unicode__(self):
        return self.name

class SomethingForm(forms.ModelForm):
    class Meta:
        model = Something

class DynamicFields(models.Model):
    refer = models.CharField(max_length=120, blank=False)
    name = models.CharField(max_length=120, blank=False)
    type = models.CharField(max_length=120, blank=False)
    max_length = models.IntegerField(null=True, blank=True)
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    required = models.BooleanField(default=True)
    choices = hstore.DictionaryField(null=True)
