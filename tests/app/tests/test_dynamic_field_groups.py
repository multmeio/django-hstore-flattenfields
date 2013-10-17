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
from decimal import Decimal

from hstore_flattenfields.forms import HStoreContentPaneModelForm
from tests.app.models import *


class OneToManyDynamicFieldGroupTests(TestCase):
    def setUp(self):
        self.group1 = SomethingType.objects.create(id=1, name="Something Group", slug="something_group")
        self.dfield1 = DynamicField.objects.create(id=1, refer="Something", group=self.group1, typo="Integer", name="something_age", verbose_name=u"Age")

        self.group2 = SomethingType.objects.create(id=2, name="Something Group2", slug="something_group2")
        
        self.dfield2 = DynamicField.objects.create(id=2, refer="Something", group=self.group2, name="something_slug", verbose_name=u"Slug", typo="CharField", max_length=100)
        self.dfield3 = DynamicField.objects.create(id=3, refer="Something", group=self.group2, name="something_info", verbose_name=u"Info", typo="CharField", max_length=100)
        self.dfield4 = DynamicField.objects.create(id=4, refer="Something", name="something_description", verbose_name=u"Description", typo="TextArea", max_length=100)

    def test_assert_all_dynamic_fields(self):
        self.something = Something.objects.create(
            name=u"Some Name",
            something_group=self.group1,
            something_age=42,
            something_slug="some-name",
        )
        self.assertEqual(
            self.something.dynamic_fields,
            [self.dfield1, self.dfield4]
        )

    def test_assert_specific_dynamic_fields(self):
        self.something = Something.objects.create(
            name=u"Some Name",
            something_group=self.group2,
            something_age=42,
            something_slug="some-name",
        )
        self.assertEqual(
            self.something.dynamic_fields,
            [self.dfield2, self.dfield3, self.dfield4]
        )

    def test_assert_change_field_name(self):
        something_type = SomethingType.objects.get(pk=1)

        self.assertEqual(something_type.slug, u'something_group')
        something_type.name = u'Something Group Change'
        something_type.save()
        self.assertEqual(something_type.slug, u'something_group_change')


class ManyToManyDynamicFieldGroupTests(TestCase):
    def setUp(self):
        self.group1 = AuthorType.objects.create(id=1, name="Author Group", slug="author_group")
        self.group2 = AuthorType.objects.create(id=2, name="Author Group 2", slug="author_group_2")

        self.dfield1 = DynamicField.objects.create(id=1, refer="Author", group=self.group1, typo="Integer", name="author_age", verbose_name=u"Age")
        self.dfield2 = DynamicField.objects.create(id=2, refer="Author", group=self.group2, name="author_name", verbose_name=u"Name", typo="CharField", max_length=100)

        self.dfield3 = DynamicField.objects.create(id=3, refer="Author", name="author_information", verbose_name=u"Information", typo="CharField", max_length=100)

    def test_assert_all_dynamic_fields(self):
        self.author = Author.objects.create(
            author_age=42,
            author_name="some-name",
        )
        self.author.author_groups.add(self.group1)
        self.author.author_groups.add(self.group2)
        self.assertEqual(
            self.author.dynamic_fields,
            [self.dfield1, self.dfield2, self.dfield3]
        )

    def test_assert_all_dynamic_fields_without_group(self):
        self.assertEqual(
            Author().dynamic_fields,
            [self.dfield3]
        )

    def test_assert_specific_dynamic_fields(self):
        self.author = Author.objects.create(
            author_age=42,
            author_name="some-name",
        )
        self.author.author_groups.add(self.group1)
        self.assertEqual(
            self.author.dynamic_fields,
            [self.dfield1, self.dfield3]
        )

class ContentPaneTests(TestCase):
    def setUp(self):
        self.content_pane = ContentPane.objects.create(name="Container", slug="container")

        self.group1 = AuthorType.objects.create(id=1, name="Author Group", slug="author_group")

        self.dfield1 = DynamicField.objects.create(id=1, refer="Author", group=self.group1,
            content_pane=self.content_pane, typo="Integer", name="author_age", verbose_name=u"Age")
        self.dfield2 = DynamicField.objects.create(id=2, refer="Author", group=self.group1,
            name="author_name", verbose_name=u"Name", typo="CharField", max_length=100)

        self.author = Author.objects.create(author_age=42, author_name="some-name")
        self.author.author_groups.add(self.group1)

        class AuthorForm(HStoreContentPaneModelForm):
            class Meta:
                model = Author
        self.AuthorForm = AuthorForm

    def test_assert_dynamic_fields_inside_content_pane(self):
        self.assertQuerysetEqual(
            self.content_pane.fields,
            [self.dfield1],
            transform=lambda x: x
        )

    def test_assert_form_fields_names(self):
        form = self.AuthorForm(instance=self.author)
        self.assertEquals(
            form.fields.keys(),
            ['author_groups', 'author_age', 'author_name']
        )

    def test_assert_fields_from_specific_content_pane(self):
        author_form = self.AuthorForm(instance=self.author)
        self.assertEquals(
            map(lambda x: x.name, author_form.filtred_fields(self.content_pane)),
            ['author_age']
        )

    def test_assert_change_field_name(self):
        content_pane = ContentPane.objects.get(pk=1)

        self.assertEqual(content_pane.slug, u'container')
        content_pane.name = u'Container Change'
        content_pane.save()
        self.assertEqual(content_pane.slug, u'container_change')

