from django.db import models
from hstore_flattenfields.models import HStoreModel

class Something(HStoreModel):
    name = models.CharField(max_length=32)


class Author(HStoreModel):
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
