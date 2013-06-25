#!/usr/bin/env python
# encoding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django import forms
from django.test import TestCase, SimpleTestCase

from datetime import date


class DateFormatTest(SimpleTestCase):
    def test_dateField(self):
        "DateFields can parse dates in the default format"
        f = forms.DateField(input_formats=["%Y-%m-%d"], localize=False)
        # Parse a date in an unaccepted format; get an error
        self.assertRaises(forms.ValidationError, f.clean, '21.12.2010')

        # Parse a date in a valid format, get a parsed result
        result = f.clean('2010-12-21')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to the same format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

        # Parse a date in a valid, but non-default format, get a parsed result
        result = f.clean('2010-12-21')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to default format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

    def test_localized_dateField(self):
        "Localized DateFields in a non-localized environment act as unlocalized widgets"
        f = forms.DateField()
        # Parse a date in an unaccepted format; get an error
        self.assertRaises(forms.ValidationError, f.clean, '21.12.2010')

        # Parse a date in a valid format, get a parsed result
        result = f.clean('21/12/2010')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to the same format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

        # Parse a date in a valid format, get a parsed result
        result = f.clean('21/12/2010')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to default format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

    def test_dateField_with_inputformat(self):
        "DateFields with manually specified input formats can accept those formats"
        f = forms.DateField(input_formats=["%d.%m.%Y", "%d-%m-%Y"], localize=False)
        # Parse a date in an unaccepted format; get an error
        self.assertRaises(forms.ValidationError, f.clean, '2010-12-21')

        # Parse a date in a valid format, get a parsed result
        result = f.clean('21.12.2010')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to the same format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

        # Parse a date in a valid format, get a parsed result
        result = f.clean('21-12-2010')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to default format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

    def test_localized_dateField_with_inputformat(self):
        "Localized DateFields with manually specified input formats can accept those formats"
        f = forms.DateField(input_formats=["%d.%m.%Y", "%d/%m/%Y"], localize=True)
        # Parse a date in an unaccepted format; get an error
        self.assertRaises(forms.ValidationError, f.clean, '2010-12-21')

        # Parse a date in a valid format, get a parsed result
        result = f.clean('21.12.2010')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to the same format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")

        # Parse a date in a valid format, get a parsed result
        result = f.clean('21.12.2010')
        self.assertEqual(result, date(2010, 12, 21))

        # Check that the parsed result does a round trip to default format
        text = f.widget._format_value(result)
        self.assertEqual(text, "21/12/2010")


