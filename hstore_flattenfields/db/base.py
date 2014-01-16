from django.db import models

try:
    ModelBase = models.Model.__metaclass__
except AttributeError:
    from django.db.models.base import ModelBase
from django.conf import settings
from django.utils.translation import ugettext as _

from django_orm.postgresql import hstore

from hstore_flattenfields.db.manager import FlattenFieldsFilterManager

class HStoreModelMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super(HStoreModelMeta, cls).__new__(
            cls, name, bases, attrs
        )

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            old_setattr(self, key, value)
        
            if value and key in self._meta.get_all_dynamic_field_names():
                dynamic_field = self._meta.get_field_by_name(key)[0]
                self._dfields.update({
                    key: dynamic_field.value_to_string(self)
                })
        new_class.__setattr__ = __setattr__

        old_delattr = new_class.__delattr__
        def __delattr__(self, key):
            if hasattr(self, '_dfields') and not key in dir(new_class):
                if key in self._dfields:
                    del self._dfields[key]
                    return
            return old_delattr(self, key)
        new_class.__delattr__ = __delattr__

        _old_meta = new_class._meta
        class _meta(object):
            def __eq__(self, other):
                return _old_meta == other

            def __getattr__(self, key):
                return getattr(_old_meta, key)

            def __setattr__(self, key, value):
                return setattr(_old_meta, key, value)

            # def init_name_map(self):
            #     _cache = _old_meta.init_name_map()
            #     for dfield in self.dynamic_fields:
            #         _cache.update(**{
            #             dfield.name: (dfield, dfield.model, True, False)
            #         })
            #     return _cache
            
            def get_all_dynamic_field_names(self):
                return map(lambda x: x.name, self.dynamic_fields)
            
            @property
            def dynamic_fields(self):
                return filter(
                    lambda x: not callable(x.db_type) and \
                              x.db_type == 'dynamic_field', 
                    self.fields
                )

            def get_all_field_names(self):
                try:
                    cache = self._name_map
                except AttributeError:
                    cache = self.init_name_map()
                names = sorted(cache.keys())
                return [val for val in names if not val.endswith('+')]
    
        new_class._meta = _meta()
        # new_meta = _meta()
        # new_class._meta.__getattr__ = new_meta.__getattr__
        # new_class._meta.dynamic_fields = new_meta.dynamic_fields
        # new_class._meta.get_all_dynamic_field_names = new_meta.get_all_dynamic_field_names

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
        if _dfields: self._dfields = _dfields

    @property
    def dynamic_fields(self):
        return self._dynamic_fields

    @property
    def content_panes(self):
        return self._content_panes

    @property
    def related_instances(self):
        return []

    def fields_without_content_panes(self):
        fields_w_cpanes = map(lambda x: x.name, 
            filter(lambda f: f.content_pane, self.dynamic_fields)
        )
        def without_cpane(f): 
            return f.name not in fields_w_cpanes
        return filter(without_cpane, self._meta.fields)

    @property
    def default_content_pane(self):
        return {
            'name': getattr(settings, 'DEFAULT_CONTENT_PANE_NAME', _('Main Information')),
            'slug': 'default',
            'pk': '',
            'model': self.__class__,
            'fields': self.fields_without_content_panes()
        }
    

class HStoreGroupedModel(HStoreModel):
    class Meta:
        abstract = True
        
    @property
    def related_instance(self):
        if self._related_instances:
            return self._related_instances[0]

    @property
    def dynamic_fields(self):
        dynamic_fields = super(HStoreGroupedModel, self).dynamic_fields

        def by_group(dynamic_field):
            related_instance = self.related_instance
            if related_instance:
                return dynamic_field.group == None or \
                    related_instance == dynamic_field.group
            try:
                if dynamic_field.group == None:
                    return True
            except:  # DoesNotExist
                return True
            else:
                return False

        return filter(by_group, dynamic_fields)

    @property
    def content_panes(self):
        content_panes = super(HStoreGroupedModel, self).content_panes

        def by_group(content_pane):
            related_instance = self.related_instance
            if related_instance:
                return content_pane.group == None or \
                    related_instance == content_pane.group
            try:
                if content_pane.group == None:
                    return True
            except:  # DoesNotExist
                return True
            else:
                return False

        return filter(by_group, content_panes)


class HStoreM2MGroupedModel(HStoreModel):
    class Meta:
        abstract = True

    @property
    def related_instances(self):
        return self._related_instances

    @property
    def dynamic_fields(self):
        dynamic_fields = super(HStoreM2MGroupedModel, self).dynamic_fields
        def by_groups(dynamic_field):
            return dynamic_field.group == None or \
                   dynamic_field.group in self.related_instances
        return filter(by_groups, dynamic_fields)

    @property
    def content_panes(self):
        content_panes = super(HStoreM2MGroupedModel, self).content_panes
        def by_groups(content_pane):
            return content_pane.group == None or \
                   content_pane.group in self.related_instances
        return filter(by_groups, content_panes)
