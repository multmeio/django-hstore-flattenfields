#!/usr/bin/env python
# encoding: utf-8

'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from django_orm.postgresql import hstore
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ManyRelatedManager
from django.core.exceptions import ValidationError
from django import forms

from fields import *
from queryset import *
from utils import *

dfields = None

class ContentPane(models.Model):
    """
    Class to contains fields reproduced into TABs, DIVs,... on templates.
    """
    name = models.CharField(max_length=80, null=False, verbose_name=u'Título')
    order = models.IntegerField(null=False, blank=False, default=0, verbose_name=u'Ordem')
    slug = models.CharField(max_length=80, null=False)

    class Meta:
        ordering = ['order', 'slug']

    def __unicode__(self):
        return u"[#%s, %s] - %s" % (self.id, self.order, self.name)

    @property
    def fields(self):
        return self.dynamic_fields.all()


class DynamicFieldGroup(models.Model):
    """
    Class context to fields in the use case.
    This has to be implemented on main app, and related to
    class HstoreModel that contains _dfields.
    """
    name = models.CharField(max_length=80, null=False, verbose_name='Name')
    slug = models.CharField(max_length=80, unique=True, null=False)
    description = models.TextField(null=True, blank=True, verbose_name=u'Description')

    def __unicode__(self):
        return u"%s" % self.name


class DynamicField(models.Model):
    refer = models.CharField(max_length=120, blank=False, db_index=True, verbose_name="Class name")
    name = models.CharField(max_length=120, blank=False, db_index=True, unique=True, verbose_name="Field name")
    verbose_name = models.CharField(max_length=120, blank=False, verbose_name="Verbose name")
    typo = models.CharField(max_length=20, blank=False, db_index=True, verbose_name="Field type",
        choices=single_list_to_tuple(FIELD_TYPES))
    max_length = models.IntegerField(null=True, blank=True, verbose_name="Length")
    order = models.IntegerField(null=True, blank=True, default=None, verbose_name="Order")
    blank = models.BooleanField(default=True, verbose_name="Blank")
    choices = models.TextField(null=True, blank=True, verbose_name="Choices")
    default_value = models.CharField(max_length=80, null=True, blank=True, verbose_name="Default value")

    # relations
    content_pane = models.ForeignKey(ContentPane, null=True, blank=True, related_name='dynamic_fields', verbose_name=u'Panel')
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name='dynamic_fields', verbose_name=u'Group')

    def __unicode__(self):
        return self.verbose_name or self.name

    @property
    def has_blank_option(self):
        return self.blank and \
            self.typo not in FIELD_TYPES_WITHOUT_BLANK_OPTION

    def save(self, *args, **kwargs):
        super(DynamicField, self).save()
        global dfields
        dfields = DynamicField.objects.all()

    def delete(self):
        super(DynamicField, self).delete()
        global dfields
        dfields = DynamicField.objects.all()

# XXX: Charge memory with all dfields for prevent flood on db.
dfields =  DynamicField.objects.all()

def find_dfields(refer=None, name=None, groups=None):
    if name and refer:
        return [dfield for dfield in dfields if dfield.refer == refer and dfield.name == name]
    elif name:
        return [dfield for dfield in dfields if dfield.name == name]
    elif refer and groups:
        return [dfield for dfield in dfields if dfield.refer == refer and dfield.group in groups]
    elif refer:
        return [dfield for dfield in dfields if dfield.refer == refer]


class HStoreModelMeta(models.Model.__metaclass__):
    def __new__(cls, name, bases, attrs):
        new_class = super(HStoreModelMeta, cls).__new__(
            cls, name, bases, attrs
        )

        # override getattr/setattr/delattr
        old_getattribute = new_class.__getattribute__
        def __getattribute__(self, key):
            field = find_dfields(name=key)
            if field:
                field = get_modelfield(field[0].typo)()
            else:
                field = None

            try:
                return old_getattribute(self, key)
            except AttributeError:
                if field:
                    try:
                        value = self._dfields[key]
                    except KeyError:
                        if hasattr(field, 'default_value'):
                            value = field.default_value
                        elif hasattr(field, 'default'):
                            value = field.default

                    return field.to_python(value)
                else:
                    raise
            except ValueError:
                if field:
                    try:
                        return field.to_python(field.default_value)
                    except AttributeError:
                        return field.to_python(field.default)
            except TypeError:
                if field and field.__class__.__name__ == 'ManyRelatedManager':
                    return field.all()
                return field
        new_class.__getattribute__ = __getattribute__

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            #print "called __setattr__(%r, %r)" % (key, value)

            if hasattr(self, '_dfields') and not hasattr(new_class, key):
                dfield = find_dfields(refer=new_class.__name__, name=key)
                if dfield:
                    # import ipdb; ipdb.set_trace()
                    value = get_modelfield(dfield[0].typo)().to_python(value)

                    # if isinstance(value, (list, tuple)):
                    #     value = [unicode(v) for v in value]
                    # elif value is not None:
                    #     value = unicode(value)
                    #NOTE: Convert Date strings to ISO format.
                    # if dfield.typo == 'Date' and value and not isinstance(value, date):
                    #     value = str2date(value)

                    self._dfields[key] = ''
                    if value is not None:
                        self._dfields[key] = unicode(value)
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


        # @property
        # def dynamic_fields(self):
        #     """
        #     Property created to return the DynamicFields of this instance.

        #     If this instance has a 'related_field', it returns his fields,
        #     if not, we will return just the fields without 'related_field' setted.

        #     XXX: Today the fields is getting from the memory...
        #     """
        #     import ipdb; ipdb.set_trace()

        #     dfields = find_dfields(refer=self.__class__.__name__)
        #     selected_dfields = []

        #     for dfield in dfields:
        #         if self.related_instance:
        #             if getattr(dfield, self.hstore_related_field) == self.related_instance or \
        #                getattr(dfield, self.hstore_related_field) == None:
        #                 selected_dfields.append(dfield)
        #         else:
        #             if getattr(dfield, self.hstore_related_field) == None:
        #                 selected_dfields.append(dfield)
        #     return selected_dfields
        # new_class.dynamic_fields = dynamic_fields


        # @property
        # def content_panes(self):
        #     return ContentPane.objects.filter(
        #         dynamic_fields__in=self.dynamic_fields
        #     ).distinct()



        # override _meta.fields (property)
        _old_meta = new_class._meta
        class _meta(object):
            def __eq__(self, other):
                return _old_meta == other

            def __getattr__(self, key):
                return getattr(_old_meta, key)

            def __setattr__(self, key, value):
                return setattr(_old_meta, key, value)

            def init_name_map(self):
                _cache = _old_meta.init_name_map()
                for dfield in self.dynamic_fields:
                    _cache.update(**{
                        dfield.name: (dfield, _old_meta.concrete_model, True, False)
                    })
                return _cache

            def get_field_by_name(self, name):
                if name is 'pk': name = 'id'
                try:
                    if hasattr(self, '_name_map') and name in self._name_map:
                        return self._name_map[name]
                    else:
                        cache = self.init_name_map()
                        return cache[name]
                except KeyError:
                    raise FieldDoesNotExist('%s has no field named %r'
                            % (self.object_name, name))

            def get_field(self, name, many_to_many=True):
                """
                Returns the requested field by name. Raises FieldDoesNotExist on error.
                """
                to_search = many_to_many and (self.fields + self.many_to_many) or self.fields
                for f in to_search:
                    if f.name == name:
                        return f
                raise FieldDoesNotExist('%s has no field named %r' % (self.object_name, name))

            def get_all_field_names(self):
                declared_and_dfields = set(get_fieldnames(self.fields, ['_dfields']))
                relation_fields = set()
                if hasattr(self, '_name_map'):
                    relation_fields = set(getattr(self, '_name_map').keys())
                all_fields = list(declared_and_dfields.union(relation_fields))
                return all_fields

            def get_all_dynamic_field_names(self):
                return get_fieldnames(self.dynamic_fields)

            @property
            def dynamic_fields(self):
                fields = []
                if not dynamic_field_table_exists():
                    return fields
                metafields = find_dfields(refer=new_class.__name__)
                for metafield in metafields:
                    try:
                        fields.append(
                            create_field_from_instance(metafield)
                        )
                    except SyntaxError:
                        raise \
                            TypeError(('Cannot create field for %r, maybe type %r ' + \
                                       'is not a django type') % (metafield, metafield.typo))
                return fields

            @property
            def fields(self):
                return _old_meta.fields + self.dynamic_fields

            def get_base_chain(self, model):
                """
                Returns a list of parent classes leading to 'model' (order from closet
                to most distant ancestor). This has to handle the case were 'model' is
                a granparent or even more distant relation.
                """
                if model in self.parents or not self.parents:
                    # FIXME: In cases of the actual Model doesn`t have
                    # Any parent, so return him
                    return [model]
                parent = None
                for parent in self.parents:
                    res = parent._meta.get_base_chain(model)
                    if res:
                        res.insert(0, parent)
                        return res
                if model.__base__ == parent:
                    return [parent]
                raise TypeError('%r is not an ancestor of this model'
                        % model._meta.module_name)

        new_class._meta = _meta()
        return new_class


class HStoreModel(models.Model):
    _dfields = hstore.DictionaryField(db_index=True, null=True, blank=True)

    __metaclass__ = HStoreModelMeta
    objects = FlattenFieldsFilterManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        _dfields = None
        if args:
            # XXX: hack in order to save _dfields without alter django
            # save _dfields in args and restore

            # what the index of _dfields?
            i = 0
            index = None
            for f in self._meta.local_fields:
                if f.name == "_dfields":
                    index = i
                    break
                i = i + 1
            if index is not None and index < len(args):
                _dfields = args[index]

        super(HStoreModel, self).__init__(*args, **kwargs)
        if _dfields:
            self._dfields = _dfields


class HStoreContentPaneModel(HStoreModel):
    hstore_related_field = None
    related_instance = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(HStoreContentPaneModel, self).__init__(*args, **kwargs)
        if self.hstore_related_field:
            self.related_instance = getattr(self, self.hstore_related_field)

            if isinstance(self.related_instance, ManyRelatedManager):
                self.related_instance = self.related_instance.all()

    @property
    def dynamic_fields(self):
        """
        Property created to return the DynamicFields of this instance.

        If this instance has a 'related_field', it returns his fields,
        if not, we will return just the fields without 'related_field' setted.

        XXX: Today the fields is getting from the memory...
        """
        dfields = find_dfields(refer=self.__class__.__name__)
        selected_dfields = []

        for dfield in dfields:
            if self.related_instance:
                if getattr(dfield, self.hstore_related_field) == self.related_instance or \
                   getattr(dfield, self.hstore_related_field) == None:
                   selected_dfields.append(dfield)
            else:
                if getattr(dfield, self.hstore_related_field) == None:
                    selected_dfields.append(dfield)
        return selected_dfields

    @property
    def content_panes(self):
        return ContentPane.objects.filter(
            dynamic_fields__in=self.dynamic_fields
        ).distinct()


class HStoreContentPaneManyToManyModel(HStoreModel):
    hstore_related_field = None
    hstore_dfield_related_field = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(HStoreContentPaneManyToManyModel, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(HStoreContentPaneManyToManyModel, self).__init__(*args, **kwargs)
        base_class = self.__class__.__base__
        hstore_classes = [HStoreModel, HStoreContentPaneManyToManyModel]

        if self.hstore_related_field:
            try:
                self.related_instance = getattr(self, self.hstore_related_field).all()
            except AttributeError:
                self.related_instance = []

        if not base_class in hstore_classes:
            related_name = "%s_ptr" % base_class.__name__.lower()

            for dfield in self.dynamic_fields:
                name = dfield.name

                if self.pk and hasattr(self.__class__, related_name):
                    parent = getattr(self, related_name)
                    value = getattr(parent, name, '')
                    setattr(self, name, value)

    @property
    def related_field(self):
        # NOTE: The name of fields in the relation of the Entity and
        #       the DynamicField Model can be differents...
        return self.hstore_dfield_related_field if \
            self.hstore_dfield_related_field else \
            self.hstore_related_field

    @property
    def dynamic_fields(self):
        """
        Property created to return the DynamicFields of this instance.

        If this instance has a 'related_field', it returns his fields,
        if not, we will return just the fields withou 'related_field' setted.

        XXX: Today the fields is getting from the memory...
        """
        dfields = find_dfields(refer=self.__class__.__name__, groups=[self.related_instance])
        selected_dfields = []
        for dfield in dfields:
            if self.related_instance:
                if dfield.dynamic_fields in self.related_instance or \
                   dfield.dynamic_fields == None:
                   selected_dfields.append(dfield)
            else:
                if getattr(dfield, self.dynamic_fields) == None:
                    selected_dfields.append(dfield)
        return selected_dfields


    @property
    def content_panes(self):
        return set([
            x.content_pane for x in self.dynamic_fields if x.content_pane
        ])

