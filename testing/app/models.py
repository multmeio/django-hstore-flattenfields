from django.db import models
from hstore_flattenfields.models import (HStoreModel, DynamicField,
                                         ContentPane, DynamicFieldGroup,
                                         HStoreGroupedModel, HStoreM2MGroupedModel)

class Something(HStoreGroupedModel):
    name = models.CharField(max_length=32)

    # relations
    something_group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name='somethings', verbose_name=u'Group')

    class Meta:
        # hstore
        hstore_related_field = 'something_group'


class Author(HStoreM2MGroupedModel):
    # relations
    author_groups = models.ManyToManyField(DynamicFieldGroup, null=True, blank=True, related_name='authors', verbose_name=u'Group')

    class Meta:
        # hstore
        hstore_related_field = 'author_groups'

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
