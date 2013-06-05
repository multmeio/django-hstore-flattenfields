#!/usr/bin/env python
# encoding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from datetime import date, datetime
from decimal import Decimal

from app.models import *
from hstore_flattenfields.models import DynamicField

class TypeTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(id=1, refer="Something", typo="Integer", name="something_dfield_int", verbose_name = u"Dynamic Field Int")
        DynamicField.objects.create(id=5, refer="Something", typo="Monetary", name="something_dfield_decimal", verbose_name=u"Dynamic Field Decimal",)
        DynamicField.objects.create(id=2, refer="Something", typo="CharField", name="something_dfield_str", verbose_name = u"Dynamic Field Str")
        DynamicField.objects.create(id=3, refer="Something", typo="Date", name="something_dfield_date", verbose_name = u"Dynamic Field Date",)
        DynamicField.objects.create(id=4, refer="Something", typo="DateTime", name="something_dfield_datetime", verbose_name=u"Dynamic Field DateTime")
        DynamicField.objects.create(id=6, refer="Something", typo="MultSelect", name="something_dfield_multiselect", verbose_name=u"Dynamic Field MultiSelect",)

        self.something = Something.objects.create(name=u"Some Name", something_dfield_int=42, something_dfield_decimal=Decimal(42.5), something_dfield_str=u"Dynamic Field Str", something_dfield_date=date.today(), something_dfield_datetime=datetime.now(), something_dfield_multiselect=['A', 'B', 'C'])

    def test_assert_int_type(self):
        value = self.something.something_dfield_int
        self.assertIsInstance(value, int)

    def test_assert_decimal_type(self):
        value = self.something.something_dfield_decimal
        self.assertIsInstance(value, Decimal)

    def test_assert_str_type(self):
        value = self.something.something_dfield_str
        self.assertIsInstance(value, unicode)

    def test_assert_date_type(self):
        value = self.something.something_dfield_date
        self.assertIsInstance(value, date)

    def test_assert_datetime_type(self):
        value = self.something.something_dfield_datetime
        self.assertIsInstance(value, datetime)

    def test_assert_multiselect_type(self):
        value = self.something.something_dfield_multiselect
        self.assertIsInstance(value, list)

