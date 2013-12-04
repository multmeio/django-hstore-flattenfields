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

from tests.app.models import *


class IllustratorInheritanceTest(TestCase):
    # FIXME: This class is broken, cause in some weird
    # objects with inheritance from a 
    # [M2M | Grouped]HStoreModel didn't fill the last
    # instance with the properly dynamic_fields.
    def setUp(self):
        self.group1 = AuthorType.objects.create(id=1, name="Something Group", slug="something_group")

        self.age = DynamicField.objects.create(id=1, refer="Illustrator", group=self.group1, 
            typo="Integer", name="illustrator_age", verbose_name=u"Age")
        self.name = DynamicField.objects.create(id=2, refer="Illustrator", group=self.group1, 
            name="illustrator_name", verbose_name=u"Name", typo="CharField", max_length=100)
        self.information = DynamicField.objects.create(id=3, refer="Illustrator", 
            name="illustrator_information", verbose_name=u"Information", typo="CharField", max_length=100)

    def test_integrity(self):
        illustrator = Illustrator.objects.create(
            illustrator_information="Some Information",
            illustrator_age=42, 
            illustrator_name="some-name",
        )
        illustrator.author_groups.add(self.group1)

        # NOTEME: Uncomment the next line to see 
        # the test fails.
        # illustrator = Illustrator.objects.get()
        
        self.assertEqual(
            illustrator.illustrator_information, 
            "Some Information"
        )
        self.assertEqual(
            illustrator.illustrator_age, 42
        )
        self.assertEqual(
            illustrator.illustrator_name, "some-name"
        )
        

class AuthorSpecializedInheritanceTests(TestCase):
    def setUp(self):
        self.group1 = AuthorType.objects.create(id=1, name="Something Group", slug="something_group")

        self.dfield1 = DynamicField.objects.create(id=1, refer="Author", group=self.group1, 
           	typo="Integer", name="author_specialized_age", verbose_name=u"Age")
        self.dfield2 = DynamicField.objects.create(id=2, refer="Author", group=self.group1, 
            name="author_specialized_name", verbose_name=u"Name", typo="CharField", max_length=100)
        self.dfield3 = DynamicField.objects.create(id=3, refer="Author", 
            name="author_specialized_information", verbose_name=u"Information", typo="CharField", max_length=100)

    def test_assert_all_dynamic_fields(self):
        self.author_specialized = Author.objects.create(
        	author_specialized_age=42, author_specialized_name="some-name"
        )
        self.author_specialized.author_groups.add(self.group1)
        self.assertEqual(
            self.author_specialized.dynamic_fields,
            [self.dfield1,  self.dfield2, self.dfield3]
        )
