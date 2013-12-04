from django.db import models
from django.db.models.fields import FieldDoesNotExist

try:
    ModelBase = models.Model.__metaclass__
except AttributeError:
    from django.db.models.base import ModelBase

from django.core.cache import cache
from django_orm.postgresql import hstore
from hstore_flattenfields.db.manager import FlattenFieldsFilterManager
from hstore_flattenfields.utils import (
    get_fieldnames,
    get_modelfield,
    dynamic_field_table_exists,
    create_field_from_instance,
    has_any_in,
    build_flattenfields_object,
)


class HStoreModelMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super(HStoreModelMeta, cls).__new__(
            cls, name, bases, attrs
        )

        # override getattr/setattr/delattr
        old_getattribute = new_class.__getattribute__

        def __getattribute__(self, key):
            try:
                return old_getattribute(self, key)
            except AttributeError:
                # queryset = cache.get('dynamic_fields', [])
                # # field = [f for f in queryset if f.name==key]
                # # field = get_dynamic_field_model().objects.find_dfields(name=key)
                # from hstore_flattenfields.models import DynamicField
                def by_name(f):
                    return f.name == key
                field = filter(by_name, self._meta.dynamic_fields)
                # field = DynamicField.objects.filter(name=key).order_by('pk')
                if field:
                    # field = get_modelfield(field[0].typo)()
                    field = field[0]
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
            except TypeError:
                # queryset = cache.get('dynamic_fields', [])
                # field = [f for f in queryset if f.name==key]
                def by_name(f):
                    return f.name == key
                field = filter(by_name, self._meta.dynamic_fields)
                if field and field.__class__.__name__ == 'ManyRelatedManager':
                    return field.all()
                return field
        new_class.__getattribute__ = __getattribute__

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            if hasattr(self, '_dfields') and not key in dir(new_class):
                # from django.core.cache import cache
                # queryset = cache.get('dynamic_fields', [])
                # dfield = [f for f in queryset if f.refer==new_class.__name__ and\
                #           f.name==key]
                # from hstore_flattenfields.models import DynamicField
                # dfield = DynamicField.objects.filter(name=key, refer=new_class.__name__)
                def by_name(f):
                    return f.name == key
                dfield = filter(by_name, self._meta.dynamic_fields)
                if dfield:
                    # value = get_modelfield(dfield[0])().to_python(value)
                    value = dfield[0].to_python(value)

                    self._dfields[key] = ''
                    if value is not None:
                        self._dfields[key] = unicode(value)
                    return
            # print "called __setattr__(%r, %r)" % (key, value)
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
                if name is 'pk':
                    name = 'id'
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
                to_search = many_to_many and (
                    self.fields + self.many_to_many) or self.fields
                for f in to_search:
                    if f.name == name:
                        return f
                raise FieldDoesNotExist(
                    '%s has no field named %r' % (self.object_name, name))

            def get_all_field_names(self):
                declared_and_dfields = set(
                    get_fieldnames(self.fields, ['_dfields']))
                relation_fields = set()
                if hasattr(self, '_name_map'):
                    relation_fields = set(getattr(self, '_name_map').keys())
                all_fields = list(declared_and_dfields.union(relation_fields))
                return all_fields

            def get_all_dynamic_field_names(self):
                return get_fieldnames(self.dynamic_fields)

            @property
            def dynamic_fields(self):
                # fields = []
                # if not dynamic_field_table_exists():
                #     return fields

                # from hstore_flattenfields.models import DynamicField
                # metafields = DynamicField.objects.filter(
                #     refer=new_class.__name__
                # ).order_by('pk')
                # return map(create_field_from_instance, metafields)
                try:
                    fields = self._model_dynamic_fields
                except AttributeError:
                    fields = []
                # for metafield in metafields:
                #     try:
                #         fields.append(
                #             create_field_from_instance(metafield)
                #         )
                #     except SyntaxError:
                #         raise \
                #             TypeError(('Cannot create field for %r, maybe type %r ' +
                #                        'is not a django type') % (metafield, metafield.typo))
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
        build_flattenfields_object(self)

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
        # dynamic_field_names = self._meta.get_all_field_names()
        # def by_name(dynamic_field):
        #     return dynamic_field.name in dynamic_field_names
        # return filter(by_name, self._dynamic_fields)
        # return filter(by_name, cache.get('dynamic_fields', []))
        # from hstore_flattenfields.models import DynamicField
        # return filter(by_name, DynamicField.objects.filter(
        #     refer=self.__class__.__name__
        # ).order_by('pk'))

    @property
    def content_panes(self):
        return self._content_panes


class HStoreGroupedModel(HStoreModel):
    class Meta:
        abstract = True

    @property
    def related_instance(self):
        return getattr(self, self._meta.hstore_related_field)

    @property
    def dynamic_fields(self):
        dynamic_fields = super(HStoreGroupedModel, self).dynamic_fields

        def by_group(dynamic_field):
            related_instance = self.related_instance
            if related_instance:
                return dynamic_field.group == None or \
                    related_instance.dynamicfieldgroup_ptr == dynamic_field.group
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
                    related_instance.dynamicfieldgroup_ptr == content_pane.group
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

    def __init__(self, *args, **kwargs):
        super(HStoreM2MGroupedModel, self).__init__(*args, **kwargs)
        # print "\t%s \n\t%s\n\n" % (self._dfields, self.dynamic_fields)
        # self._is_cached = False
        # if not cache.get(self.custom_cache_key):
        #     self._cache_builder()

        if not self.pk:
            return

        base_class = self.__class__.__base__
        hstore_classes = [HStoreModel, HStoreM2MGroupedModel]

        if not base_class in hstore_classes:
            related_name = "%s_ptr" % base_class.__name__.lower()

            for dfield in self.dynamic_fields:
                name = dfield.name

                if hasattr(self.__class__, related_name):
                    parent = getattr(self, related_name)
                    value = getattr(parent, name, '')
                    setattr(self, name, value)

    # def __del__(self, *args, **kwargs):
    #     cache.delete(self.custom_cache_key)
    #     super(HStoreM2MGroupedModel, self).__del__(*args, **kwargs)

    # @property
    # def custom_cache_key(self):
    #     return "%s_%s" % (self._meta.hstore_related_field, self.pk)

    # def _cache_builder(self):
    #     self._is_cached = False
    #     try:
    #         related_instances = getattr(
    #             self, self._meta.hstore_related_field
    #         ).prefetch_related('dynamicfieldgroup_ptr')
    #     except (AttributeError, ValueError):
    #         # NOTE: The AttributeError, ValueError is raised when
    #         #       We Try to add a HStoreModel object and him
    #         #       do not have pk or was not filled out by the Django
    #         pass
    #     else:
    #         cache.set(self.custom_cache_key, related_instances)
    #         self._is_cached = True

    @property
    def related_instances(self):
        # if not cache.get(self.custom_cache_key):
        # if not self._is_cached:
        #     # NOTE: We had to rebuild the cache in this case
        #     #       because in this case, we can just retrieve the
        #     #       DynamicFieldGroup`s after the object get his id
        #     self._cache_builder()
        # instances = cache.get(self.custom_cache_key)
        try:
            instances = getattr(
                self, self._meta.hstore_related_field
            ).prefetch_related('dynamicfieldgroup_ptr')
        except (AttributeError, ValueError):
            instances = None

        from django.db.models.query import QuerySet
        if not isinstance(instances, QuerySet):
            return []

        from hstore_flattenfields.models import DynamicFieldGroup
        QueryModel = instances.query.model


        if QueryModel != DynamicFieldGroup and \
           issubclass(QueryModel, DynamicFieldGroup):
            instances = map(lambda x: x.dynamicfieldgroup_ptr, instances)
        return instances

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
        # from hstore_flattenfields.models import ContentPane
        # def by_group_in_dfields(dynamic_field):
        #     instances = self.related_instances
        #     if instances:
        #         return bool([x for x in instances if dynamic_field.group == None or
        #                      x == dynamic_field.group])
        #     try:
        #         if dynamic_field.group == None:
        #             return True
        #     except:  # DoesNotExist
        #         return True
        #     else:
        #         return False

        # def by_group(content_pane):
        #     return any(filter(by_group_in_dfields, content_pane.fields))

        # def by_dfields(content_pane):
        #     cpane_fields_pks = map(lambda f: f.pk, content_pane.fields)
        #     obj_fields_pks = map(lambda f: f.pk, self.dynamic_fields)

        #     return has_any_in(cpane_fields_pks, obj_fields_pks)

        # def by_refer(content_pane):
        #     return content_pane.content_type.model == self.__class__.__name__.lower()

        # content_panes = cache.get('content_panes', [])

        # content_panes = filter(by_refer, content_panes)
        # content_panes = filter(by_group, content_panes)
        # content_panes = filter(by_dfields, content_panes)

        # return content_panes
