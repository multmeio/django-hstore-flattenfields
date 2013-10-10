#!/usr/bin/env python
# encoding: utf-8

'''
Created on 13/10/2012

@author: iuri
'''

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from django_orm.postgresql import hstore
from django_extensions.db.fields import AutoSlugField

from db.manager import CacheDynamicFieldManager
from db.base import (
    HStoreModel,
    HStoreM2MGroupedModel,
)
from hstore_flattenfields.utils import (
    single_list_to_tuple,
    FIELD_TYPES,
    FIELD_TYPES_WITHOUT_BLANK_OPTION,
)


# Setup the "class Meta:" flattenfields custom configs
models.options.DEFAULT_NAMES += (
    'hstore_related_field',
)

class DynamicFieldGroup(models.Model):
    """
    Class context to fields in the use case.
    This has to be implemented on main app, and related to
    class HstoreModel that contains _dfields.
    """
    name = models.CharField(max_length=80, null=False, verbose_name=_('Name'))
    slug = AutoSlugField(populate_from='name', separator='_', max_length=100, unique=True, overwrite=True)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Dynamic Field Group')
        verbose_name_plural = _('Dynamic Field Groups')

    @property
    def fields(self):
        return DynamicField.objects.find_dfields(group=self)

    def __unicode__(self):
        return u"%s" % self.name


class ContentPane(models.Model):
    """
    Class to contains fields reproduced into TABs, DIVs,... on templates.
    """
    name = models.CharField(max_length=80, null=False, verbose_name=_('Name'))
    order = models.IntegerField(null=False, blank=False, default=0, verbose_name=_('Order'))
    slug = AutoSlugField(populate_from='name', separator='_',max_length=100, unique=True, overwrite=True)

    # relations
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name='content_panes')
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name="content_panes", verbose_name=_("Groups"))

    class Meta:
        verbose_name = _('Content Pane')
        verbose_name_plural = _('Content Panes')

    def __unicode__(self):
        return u"[#%s, %s] - %s" % (self.id, self.order, self.name)

    @property
    def fields(self):
        return DynamicField.objects.find_dfields(cpane=self)


class DynamicField(models.Model):
    refer = models.CharField(max_length=120, blank=False, db_index=True, verbose_name=_("Class name"))
    name = models.CharField(max_length=120, blank=False, db_index=True,unique=True, verbose_name=_("Field name"))
    verbose_name = models.CharField(max_length=120, blank=False, verbose_name=_("Verbose name"))
    typo = models.CharField(max_length=20, blank=False, db_index=True, verbose_name=_("Field type"), choices=single_list_to_tuple(FIELD_TYPES))
    max_length = models.IntegerField(null=True, blank=True, verbose_name=_("Length"))
    order = models.IntegerField(null=True, blank=True, default=None, verbose_name=_("Order"))
    blank = models.BooleanField(default=True, verbose_name=_("Blank"))
    choices = models.TextField(null=True, blank=True, verbose_name=_("Choices"))
    default_value = models.CharField(max_length=80, null=True, blank=True, verbose_name=_("Default value"))
    help_text = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Help Text'))
    html_attrs = hstore.DictionaryField(db_index=True, null=True, blank=True, default=None, verbose_name=_("html Attributes"))

    # relations
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name="dynamic_fields", verbose_name=_("Groups"))
    content_pane = models.ForeignKey(ContentPane, null=True, blank=True, related_name="dynamic_fields", verbose_name=_("Panel"))

    objects = CacheDynamicFieldManager()

    class Meta:
        verbose_name = _('Dynamic Field')
        verbose_name_plural = _('Dynamic Fields')

    def __unicode__(self):
        return self.verbose_name or self.name

    @property
    def has_blank_option(self):
        return self.blank and \
            self.typo not in FIELD_TYPES_WITHOUT_BLANK_OPTION

    def save(self, *args, **kwargs):
        super(DynamicField, self).save()
        global dfields
        dfields = self.__class__.objects.all()

    def delete(self):
        super(DynamicField, self).delete()
        global dfields
        dfields = self.__class__.objects.all()

dfields = DynamicField.objects.all()
