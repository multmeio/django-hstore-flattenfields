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

from tests.app.models import *


class TypeDateObjectLevelTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(id=3, refer="Something", blank=False, typo="Date", name="something_dfield_date", verbose_name = u"Dynamic Field Date",)
        self.something = Something.objects.create(
            name=u"Some Name",
        )

    def test_assert_date_type(self):
        self.something.something_dfield_date = date.today()
        self.something.save()
        self.assertIsInstance(self.something.something_dfield_date, date)

    def test_assert_date_string_iso_type(self):
        self.something.something_dfield_date = str(date.today())
        self.something.save()
        self.assertIsInstance(self.something.something_dfield_date, date)

    def test_assert_date_string_br_type(self):
        self.something.something_dfield_date = date.today().strftime("%d/%m/%Y")
        self.something.save()
        self.assertIsInstance(self.something.something_dfield_date, date)

    def test_assert_invalid_date_string_type(self):
        iso_today = str(date.today())
        iso_today = iso_today.replace(iso_today[-2:], '50')
        with self.assertRaises(ValueError):
            self.something.something_dfield_date = iso_today
            self.assertEqual(self.something.something_dfield_date, iso_today)
            # self.assertRaises(ValueError, self.something.save)
            self.assertIsInstance(self.something.something_dfield_date, date)


class TypeCreateManagerTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(id=1, refer="Something", typo="Integer", name="something_dfield_int", verbose_name = u"Dynamic Field Int")
        DynamicField.objects.create(id=2, refer="Something", typo="CharField", name="something_dfield_str", verbose_name = u"Dynamic Field Str")
        DynamicField.objects.create(id=3, refer="Something", typo="Date", name="something_dfield_date", verbose_name = u"Dynamic Field Date",)
        DynamicField.objects.create(id=4, refer="Something", typo="DateTime", name="something_dfield_datetime", verbose_name=u"Dynamic Field DateTime")
        DynamicField.objects.create(id=5, refer="Something", typo="Monetary", name="something_dfield_decimal", verbose_name=u"Dynamic Field Decimal",)
        DynamicField.objects.create(id=6, refer="Something", typo="MultSelect", name="something_dfield_multiselect", verbose_name=u"Dynamic Field MultiSelect",)
        DynamicField.objects.create(id=7, refer="Something", typo="RadioButton", name="something_dfield_radiobutton", verbose_name=u"Dynamic Field RadioButton", choices=['1', '2', '3', '4'])
        DynamicField.objects.create(id=8, refer="Something", typo="CheckBox", name="something_dfield_checkbox", verbose_name=u"Dynamic Field CheckBox", choices=['1', '2', '3', '4'])

        self.something = Something.objects.create(
            name=u"Some Name",
            something_dfield_int=42,
            something_dfield_decimal=Decimal(42.5),
            something_dfield_str=u"Dynamic Field Str",
            something_dfield_date=date.today(),
            something_dfield_datetime=datetime.now(),
            something_dfield_multiselect=['A', 'B', 'C'],
            something_dfield_radiobutton='2',
            something_dfield_checkbox=['1', '2', '3'],
        )

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

    def test_assert_radiobutton_type(self):
        value = self.something.something_dfield_radiobutton
        self.assertIsInstance(value, basestring)

    def test_assert_checkbox_type(self):
        value = self.something.something_dfield_checkbox
        self.assertIsInstance(value, list)