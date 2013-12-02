#!/usr/bin/env python
# encoding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, datetime

from hstore_flattenfields.models import ContentPane, DynamicField
from tests.app.models import AuthorType, Author

from hstore_flattenfields.utils import get_ctype

class AuthorContentPaneTests(TestCase):
    def setUp(self):
        self.commics_authors = AuthorType.objects.create(
            id=1, name="Something Group", slug="commics_authors"
        )
        self.dramatic_authors = AuthorType.objects.create(
            id=2, name="Other Group", slug="dramatic_authors"
        )

        self.main_info_pane = ContentPane.objects.create(
            id=1,
            name='Main Info', content_type=get_ctype(Author),
        )
        self.commic_pane = ContentPane.objects.create(
            id=2, name='Commic Information Pane', 
            content_type=get_ctype(Author),
            group=self.commics_authors.dynamicfieldgroup_ptr
        )
        self.dramatic_pane = ContentPane.objects.create(
            id=3, name='Drama Information Pane', 
            content_type=get_ctype(Author),
            group=self.dramatic_authors.dynamicfieldgroup_ptr
        )

        self.age = DynamicField.objects.create(
            id=1, refer="Author", 
            typo="Integer", name="author_age", 
            verbose_name=u"Age",
            content_pane=self.main_info_pane
        )
        self.name = DynamicField.objects.create(
            id=2, refer="Author", 
            name="author_name", verbose_name=u"Name", 
            content_pane=self.main_info_pane
        )
        self.information = DynamicField.objects.create(
            id=3, refer="Author", name="author_information", 
            verbose_name=u"Information", 
            group=self.commics_authors.dynamicfieldgroup_ptr
        )
        self.dramatic_level = DynamicField.objects.create(
            id=4, refer="Author", name="author_dramatic_level", 
            typo="Integer", verbose_name=u"Dramatic Level", 
            content_pane=self.main_info_pane,
            group=self.dramatic_authors.dynamicfieldgroup_ptr
        )

    def test_assert_content_pane_fields(self):
        self.assertQuerysetEqual(
            self.main_info_pane.fields,
            [
                '<DynamicField: Dramatic Level>', 
                '<DynamicField: Name>', 
                '<DynamicField: Age>'
            ]
        )

    def test_assert_object_content_panes(self):
        author = Author.objects.create(
            author_age=42, author_name="some-name"
        )
        self.assertQuerysetEqual(
            author.content_panes,
            ['<ContentPane: Main Info>']
        )

    def test_assert_groupped_content_panes(self):
        author = Author.objects.create(
            pk=777,
            author_age=42, author_name="some-name"
        )
        author.author_groups.add(self.commics_authors)
        
        self.assertQuerysetEqual(
            author.content_panes,
            [
                '<ContentPane: Commic Information Pane>', 
                '<ContentPane: Main Info>'
            ]
        )
        self.assertQuerysetEqual(
            author.dynamic_fields,
            [
                '<DynamicField: Age>', 
                '<DynamicField: Name>', 
                '<DynamicField: Information>'
            ]
        )
