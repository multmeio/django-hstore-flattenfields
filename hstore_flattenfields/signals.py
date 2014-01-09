from django.db.models.signals import pre_init, post_init
from django.db.models import Q
from django.dispatch import receiver

from hstore_flattenfields.db.base import HStoreModel
from hstore_flattenfields.utils import *

@receiver(pre_init)
def fill_model_with_fields(sender, **kwargs):
    if issubclass(sender, HStoreModel):
        try:
            from hstore_flattenfields.models import (
                DynamicField, ContentPane
            )
            assert dynamic_field_table_exists()
        except (AssertionError, ImportError):
            content_panes = metafields = []
        else:
            metafields = DynamicField.objects.filter(
                refer=sender.__name__
            ).order_by('pk').select_related('group', 'content_pane')
            content_panes = ContentPane.objects.filter(
                content_type__model=sender.__name__.lower()
            )
        for dynamic_field in metafields:
            field = create_field_from_instance(dynamic_field)
            if not field.name in sender._meta.get_all_field_names():
                field.contribute_to_class(sender, field.name)
        setattr(sender, '_dynamic_fields', metafields)
        setattr(sender, '_content_panes', content_panes)
        
@receiver(post_init)
def setup_fields_in_instance(sender, instance, **kwargs):
    if issubclass(sender, HStoreModel):
       	from hstore_flattenfields.models import DynamicFieldGroup
        try:
            instances = getattr(
                instance, instance._meta.hstore_related_field
            )
        except (AttributeError, ValueError):
            instances = []
        
        if instances.__class__.__name__ == 'ManyRelatedManager':    
            instances = instances.prefetch_related('dynamicfieldgroup_ptr')
            QueryModel = instances.query.model
        else:
            QueryModel = instances.__class__
            if instances:
                instances = [instances]

        if QueryModel != DynamicFieldGroup and \
           issubclass(QueryModel, DynamicFieldGroup):
            instances = map(lambda x: x.dynamicfieldgroup_ptr, instances)
        setattr(instance, '_related_instances', instances)

        instance_dfields = map(lambda x: x.name, instance.dynamic_fields)
        for dynamic_field in instance._meta.dynamic_fields:
            name = dynamic_field.name
            value = None
            if hasattr(instance, '_dfields') and name in instance_dfields:
                value = dynamic_field.to_python(
                    instance._dfields.get(name, dynamic_field.default)
                )
            setattr(instance, name, value)