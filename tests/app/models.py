from django.db import models

from hstore_flattenfields.db.base import *
from hstore_flattenfields.models import *

class SomethingType(DynamicFieldGroup):
    pass


class AuthorType(DynamicFieldGroup):
    pass


class Something(HStoreGroupedModel):
    name = models.CharField(max_length=32)

    # relations
    something_group = models.ForeignKey(SomethingType, null=True, blank=True, related_name='somethings', verbose_name=u'Group')

    class Meta:
        # hstore
        hstore_related_field = 'something_group'


class Author(HStoreM2MGroupedModel):
    # relations
    author_groups = models.ManyToManyField(AuthorType, null=True, blank=True, related_name='authors', verbose_name=u'Group')

    class Meta:
        # hstore
        hstore_related_field = 'author_groups'

    def __str__(self):
        if hasattr(self, 'author_name'):
            return self.author_name
        else:
            return super(Author, self).__str__()


class Tag(HStoreModel):
    articles = models.ManyToManyField('Book')

    def __str__(self):
        if hasattr(self, 'tag_name'):
            return self.tag_name
        else:
            return super(Author, self).__str__()



class Book(HStoreModel):
    author = models.ForeignKey('Author', null=True, blank=True)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        else:
            return "Book %s" % self.pk


class Season(HStoreModel):
    def __str__(self):
        if hasattr(self, 'year'):
            return self.year
        else:
            return super(Author, self).__str__()


class Game(HStoreModel):
    season = models.ForeignKey(Season, related_name='games')

    def __str__(self):
        if hasattr(self, 'away') and hasattr(self, 'home') :
            return "%s at %s" % (self.away, self.home)
        else:
            return super(Author, self).__str__()


class Player(HStoreModel):
    games = models.ManyToManyField(Game, related_name='players')

    def __str__(self):
        if hasattr(self, 'player_name'):
            return self.player_name
        else:
            return super(Author, self).__str__()
