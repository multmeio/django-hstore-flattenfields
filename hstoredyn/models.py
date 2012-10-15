'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from django import forms

from django_orm.postgresql import hstore
from django.utils.datastructures import SortedDict
import copy

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
class MyModelMeta(models.Model.__metaclass__):
    def __new__(cls, name, bases, attrs):
        super_new = super(MyModelMeta, cls).__new__

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
            #print "called __setattr__(%r, %r, %r)" % (self, key, value)
            if hasattr(self, '_dfields') and not key in dir(new_class):
                # XXX: search for key on table, django will call this method on many times on 
                #      __init__
                if DynamicFields.objects.filter(refer=new_class.__name__, name=key):
                    self._dfields[key] = value

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

    #def __init__(self, *args, **kwargs):
    # 

#######################################################
def dynfields_for_model(model, fields=None, exclude=None, widgets=None, formfield_callback=None):
    """
    based on django fields_for_model
     
    Returns a ``SortedDict`` containing form fields for the given model.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned fields.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned fields, even if they are listed
    in the ``fields`` argument.
    """
    field_list = []
    ignored = []
    refer = model.__name__

    for metafield in DynamicFields.objects.filter(refer=refer):
        type_ = metafield.type
        try:
            field_klass = eval('models.%s' % type_)
            kwargs = dict()
            f = field_klass(name=metafield.name,
                            max_length=metafield.max_length,
                            choices=metafield.choices.get('choices'),
                            blank=metafield.blank,
                            null=metafield.null)
        except:
            raise TypeError('Cannot create field for %r, maybe type %r ' + \
                            'is not a django type' % (metafield, type_))

        if not f.editable:
            continue
        if fields is not None and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if widgets and f.name in widgets:
            kwargs = {'widget': widgets[f.name]}
        else:
            kwargs = {}

        if formfield_callback is None:
            formfield = f.formfield(**kwargs)
        elif not callable(formfield_callback):
            raise TypeError('formfield_callback must be a function or callable')
        else:
            formfield = formfield_callback(f, **kwargs)

        if formfield:
            field_list.append((f.name, formfield))
        else:
            ignored.append(f.name)
    field_dict = SortedDict(field_list)
    if fields:
        field_dict = SortedDict(
            [(f, field_dict.get(f)) for f in fields
                if ((not exclude) or (exclude and f not in exclude)) and (f not in ignored)]
        )
    return field_dict
######################################

class MyModelFormMeta(forms.ModelForm.__metaclass__):
    def __new__(cls, name, bases, attrs):
        super_new = super(MyModelFormMeta, cls).__new__

        # create it
        new_class = super_new(cls, name, bases, attrs)

        # pos create, remove _dfields
        if '_dfields' in new_class.base_fields:
            new_class.base_fields.pop('_dfields')
        # return it
        return new_class


class MyModelForm(forms.ModelForm):
    __metaclass__ = MyModelFormMeta
    def __init__(self, *args, **kwargs):
        # add dynamic fields to form
        opts = self._meta
        if opts.model:
            # If a model is defined, extract dynamic form fields from it.
            if not opts.exclude:
                opts.exclude = []
            # hide dfields
            opts.exclude.append('_dfields')
            dynamic_fields = dynfields_for_model(opts.model, opts.fields,
                                      opts.exclude, opts.widgets)
            self.base_fields = copy.deepcopy(self.base_fields)
            self.base_fields.update(dynamic_fields)

        super(MyModelForm, self).__init__(*args, **kwargs)


#######################################################

class Something(MyModel):
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name

class SomethingForm(MyModelForm):
    class Meta:
        model = Something


