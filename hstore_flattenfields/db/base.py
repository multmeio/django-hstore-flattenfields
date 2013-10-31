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
    # get_dynamic_field_model,
    dynamic_field_table_exists,
    create_field_from_instance,
)


class HStoreModelMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super(HStoreModelMeta, cls).__new__(
            cls, name, bases, attrs
        )

        # override getattr/setattr/delattr
        old_getattribute = new_class.__getattribute__

        def __getattribute__(self, key):
            # from django.core.cache import cache
            queryset = cache.get('dynamic_fields')
            field = [f for f in queryset if f.name==key]
            # field = get_dynamic_field_model().objects.find_dfields(name=key)
            if field:
                field = get_modelfield(field[0].typo)()

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
            except TypeError:
                if field and field.__class__.__name__ == 'ManyRelatedManager':
                    return field.all()
                return field
        new_class.__getattribute__ = __getattribute__

        old_setattr = new_class.__setattr__
        def __setattr__(self, key, value):
            if key == 'cache_key':
                return
            if hasattr(self, '_dfields') and not key in dir(new_class):
                # from django.core.cache import cache
                queryset = cache.get('dynamic_fields')
                dfield = [f for f in queryset if f.refer==new_class.__name__ and\
                          f.name==key]
                if dfield:
                    value = get_modelfield(dfield[0])().to_python(value)

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
                fields = []
                if not dynamic_field_table_exists():
                    return fields
                # from django.core.cache import cache
                queryset = cache.get('dynamic_fields')
                try:
                    metafields = [f for f in queryset if f.refer==new_class.__name__]
                except:
                    import ipdb; ipdb.set_trace()

                # metafields = get_dynamic_field_model().objects.find_dfields(
                #     refer=new_class.__name__)

                for metafield in metafields:
                    try:
                        fields.append(
                            create_field_from_instance(metafield)
                        )
                    except SyntaxError:
                        raise \
                            TypeError(('Cannot create field for %r, maybe type %r ' +
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
        if _dfields: self._dfields = _dfields

    @property
    def dynamic_fields(self):
        return self.__class__._meta.dynamic_fields


class HStoreGroupedModel(HStoreModel):
    class Meta:
        abstract = True

    @property
    def related_instance(self):
        return getattr(self, self._meta.hstore_related_field)

    @property
    def dynamic_fields(self):
        from django.core.cache import cache
        refer = self.__class__.__name__

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
        def by_refer(dynamic_field):
            return dynamic_field.refer == refer

        return filter(
            by_group, 
            filter(by_refer, cache.get('dynamic_fields'))
        )


class HStoreM2MGroupedModel(HStoreModel):
    class Meta:
        abstract = True

    @property
    def cache_key(self):
        return "bla"

    def __init__(self, *args, **kwargs):
        super(HStoreM2MGroupedModel, self).__init__(*args, **kwargs)
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

        # from django.core.cache import cache
        self.cache_key = "%s_%s" % (self._meta.hstore_related_field, self.pk)
        if not cache.get(self.cache_key):
            related_instances = getattr(self, self._meta.hstore_related_field).all().\
                select_related('dynamicfieldgroup_ptr')
            cache.set(self.cache_key, related_instances)

    def __del__(self, *args, **kwargs):
        # from django.core.cache import cache
        cache.delete(self.cache_key)
        super(HStoreM2MGroupedModel, self).__del__(*args, **kwargs)

    @property
    def related_instances(self):
        # print "CacheKey: %s" % self.cache_key
        # from django.core.cache import cache
        instances = cache.get(self.cache_key)
        if not instances:
            return []

        from hstore_flattenfields.models import DynamicFieldGroup
        QueryModel = instances.query.model
        if QueryModel != DynamicFieldGroup and \
           issubclass(QueryModel, DynamicFieldGroup):
            return map(lambda x: x.dynamicfieldgroup_ptr, instances)




        # from hstore_flattenfields.models import DynamicFieldGroup
        # instances = []
        # try:
        #     instances = getattr(self, self._meta.hstore_related_field).all()

        #     # NOTE: In cases of Inheritance between DynamicFieldGroup
        #     # we had to get the parent of that instances to the rest of Query work on.
        #     QueyrModel = instances.query.model
        #     if QueyrModel != DynamicFieldGroup and \
        #        issubclass(QueyrModel, DynamicFieldGroup):
        #         instances = map(lambda x: x.dynamicfieldgroup_ptr, instances)
        # except (AttributeError, ValueError):
        #     pass
        # return instances

    @property
    def dynamic_fields(self):
        refer = self.__class__.__name__
        def by_group(dynamic_field):
            instances = self.related_instances
            if instances:
                return bool([x for x in instances if dynamic_field.group == None or
                             x == dynamic_field.group])
            try:
                if dynamic_field.group == None:
                    return True
            except:  # DoesNotExist
                return True
            else:
                return False

        # from django.core.cache import cache
        queryset = cache.get('dynamic_fields')
        return filter(by_group, [f for f in queryset if f.refer==refer])
        # return filter(by_group, get_dynamic_field_model().objects.find_dfields(refer=refer))
        # return queryset.filter(refer=refer, models.Q(group__in=self.related_instances) | models.Q(group__isnull=True))

    @property
    def cache_content_panes(self):
        from hstore_flattenfields.models import ContentPane
        def by_group_in_dfields(dynamic_field):
            instances = self.related_instances
            if instances:
                return bool([x for x in instances if dynamic_field.group == None or
                             x == dynamic_field.group])
            try:
                if dynamic_field.group == None:
                    return True
            except:  # DoesNotExist
                return True
            else:
                return False

        def by_group(content_pane):
            return any(filter(by_group_in_dfields, content_pane.dynamic_fields))


        def by_dfields(content_pane):
            return has_any_in(content_pane.dynamic_fields, self.dynamic_fields)

        # from django.core.cache import cache
        queryset = cache.get('content_panes')
        content_panes = [cp for cp in queryset if cp.content_type.model==self.__class__.__name__.lower()]
        content_panes = filter(by_group, content_panes)
        content_panes = filter(by_dfields, content_panes)

        return content_panes
        # return queryset.filter(
        #         models.Q(content_type__model=self.__class__.__name__.lower()),
        #         models.Q(dynamic_fields__group__in=self.related_instances) |\
        #         models.Q(dynamic_fields__group__isnull=True) &\
        #         models.Q(dynamic_fields__in=self.dynamic_fields)
        #     ).prefetch_related('dynamic_fields').\
        #       select_related('dynamicfieldgroup').distinct()
