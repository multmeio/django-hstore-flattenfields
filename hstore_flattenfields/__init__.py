from django.db.models.signals import pre_init

from models import find_dfields
from fields import crate_field_from_instance

# xxx: NOT IMPLEMENTED YET
# def add_dynamic_fields(sender, *args, **kwargs):
#     if sender.__name__ in ["Contact", "Organization"]:
#         fields = []

#         for dynamic_field in find_dfields(refer=sender.__name__):
#             field = crate_field_from_instance(dynamic_field)
#             print field.name
#             field.contribute_to_class(sender, field.name)

#             fields.append(field)

#         if fields:
#             setattr(sender.Meta, 'dynamic_fields', fields)


# pre_init.connect(add_dynamic_fields)
