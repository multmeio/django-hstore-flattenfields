from django.db import models
from hstore_flattenfields.models import (HStoreModel, BaseDynamicField, 
                                         ContentPane, BaseDynamicFieldGroup,
                                         HStoreGroupedModel, HStoreM2MGroupedModel)


class DynamicFieldGroup(BaseDynamicFieldGroup):

    class Meta:
        verbose_name = 'DynamicFieldGroup'
        verbose_name_plural = 'DynamicFieldGroups'


class DynamicField(BaseDynamicField):
    # TODO: Define fields here

    # relations
    content_pane = models.ForeignKey(ContentPane, null=True, blank=True, related_name='dynamic_fields', verbose_name=u'Panel')
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name='dynamic_fields', verbose_name=u'Group')

    class Meta:
        db_table = 'dynamic_field'
        verbose_name = 'DynamicField'
        verbose_name_plural = 'DynamicFields'


class Something(HStoreGroupedModel):
    name = models.CharField(max_length=32)

    # relations
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name='somethings', verbose_name=u'Group')

    class Meta:
        # hstore
        hstore_related_field = 'group'
        hstore_related_class_field = 'group'


class Author(HStoreM2MGroupedModel):
    # relations
    groups = models.ManyToManyField(DynamicFieldGroup, null=True, blank=True, related_name='authors', verbose_name=u'Group')

    class Meta:
        # hstore
        hstore_related_field = 'groups'
        hstore_related_class_field = 'group'

    def __str__(self):
        if self.author_name:
            return self.author_name


class Tag(HStoreModel):
    articles = models.ManyToManyField('Book')

    def __str__(self):
        if self.tag_name:
            return self.tag_name


class Book(HStoreModel):
    author = models.ForeignKey('Author', null=True, blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title or "Book %s" % self.pk


class Season(HStoreModel):
    def __str__(self):
        if self.year:
            return self.year


class Game(HStoreModel):
    season = models.ForeignKey(Season, related_name='games')

    def __str__(self):
        if self.away and self.home:
            return "%s at %s" % (self.away, self.home)


class Player(HStoreModel):
    games = models.ManyToManyField(Game, related_name='players')

    def __str__(self):
        if self.player_name:
            return self.player_name
