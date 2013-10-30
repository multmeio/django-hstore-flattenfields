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
            [self.dfield1, self.dfield2, self.dfield3]
        )
