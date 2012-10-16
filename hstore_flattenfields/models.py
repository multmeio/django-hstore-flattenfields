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

class DynamicFields(models.Model):
    refer = models.CharField(max_length=120, blank=False)
    name = models.CharField(max_length=120, blank=False)
    type = models.CharField(max_length=120, blank=False)
    max_length = models.IntegerField(null=True, blank=True)

    null = models.BooleanField(default=False)
    blank = models.BooleanField(default=False)
    choices = hstore.DictionaryField(null=True)

    objects = hstore.HStoreManager()

######################################
class HStoreModelMeta(models.Model.__metaclass__):
    def __new__(cls, name, bases, attrs):
        super_new = super(HStoreModelMeta, cls).__new__

        # create it
        new_class = super_new(cls, name, bases, attrs)

        # pos create

        # override getattr/setattr/delattr
        old_getattribute = new_class.__getattribute__
        def __getattribute__(self, key):
            try:
                return old_getattribute(self, key)
            except AttributeError:
                if hasattr(self, '_dfields') and key in self._dfields:
                    return self._dfields[key]
                raise

        new_class.__getattribute__ = __getattribute__

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            #print "called __setattr__(%r, %r)" % (key, value)

            if hasattr(self, '_dfields') and not key in dir(new_class):
                # XXX: search for key on table, django will call this method on many times on 
                #      __init__
                if DynamicFields.objects.filter(refer=new_class.__name__, name=key):
                    self._dfields[key] = str(value)
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

        # override _meta.fields (property)
        _old_meta = new_class._meta
        class _meta(object):
            @property
            def dynamic_fields(self):
                fields = []
                for metafield in DynamicFields.objects.filter(refer=new_class.__name__):
                    type_ = metafield.type
                    try:
                        #FIXME: eval is the evil, use module package
                        field_klass = eval('models.%s' % type_)
                        field = field_klass(name=metafield.name,
                                            max_length=metafield.max_length,
                                            choices=metafield.choices.get('choices'),
                                            blank=metafield.blank,
                                            null=metafield.null)
                        field.attname = metafield.name
                        fields.append(field)
                    except:
                        raise \
                            TypeError(('Cannot create field for %r, maybe type %r ' + \
                                       'is not a django type') % (metafield, type_))

                return fields

            @property
            def fields(self):
                #add dynamic_fields from table
                return _old_meta.fields + self.dynamic_fields

            def __getattr__(self, key):
                return getattr(_old_meta, key)
            def __setattr__(self, key, value):
                return setattr(_old_meta, key, value)
        new_class._meta = _meta()

        # return it
        return new_class

class HStoreModel(models.Model):
    __metaclass__ = HStoreModelMeta
    objects = hstore.HStoreManager()
    _dfields = hstore.DictionaryField(db_index=True)
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(HStoreModel, self).__init__(*args, **kwargs)


class HStoreModelFormMeta(forms.ModelForm.__metaclass__):
    def __new__(cls, name, bases, attrs):
        super_new = super(HStoreModelFormMeta, cls).__new__

        # create it
        new_class = super_new(cls, name, bases, attrs)

        # pos create, remove _dfields
        if '_dfields' in new_class.base_fields:
            new_class.base_fields.pop('_dfields')
        # return it
        return new_class


class HStoreModelForm(forms.ModelForm):
    __metaclass__ = HStoreModelFormMeta
    def __init__(self, *args, **kwargs):
        super(HStoreModelForm, self).__init__(*args, **kwargs)
        # Always override for fields (dynamic fields maybe deleted/included) 
        opts = self._meta
        if opts.model and issubclass(opts.model, HStoreModel):
            # If a model is defined, extract dynamic form fields from it.
            if not opts.exclude:
                opts.exclude = []
            # hide dfields
            opts.exclude.append('_dfields')
            self.fields = fields_for_model(opts.model, opts.fields,
                                              opts.exclude, opts.widgets)



