#!/usr/bin/env python
# encoding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import django
DJANGO_VERSION = django.VERSION[:2]
from django import forms
# from django.test import TestCase
from django.conf import settings
from datetime import date, datetime
from decimal import Decimal

from hstore_flattenfields.forms import HStoreModelForm
from hstore_flattenfields.models import DynamicField
from hstore_flattenfields.db.cache import TestCase

from tests.app.models import *


class SomethingForm(HStoreModelForm):
    class Meta:
        model = Something

class DateFormatTest(TestCase):
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


class SomethingFormRenderTest(TestCase):
    def setUp(self):
        DynamicField.objects.create(id=1, refer="Something", typo="Integer", name="something_dfield_integer", verbose_name = u"Dynamic Field Int", html_attrs={'data-mask': 'integer'})
        DynamicField.objects.create(id=2, refer="Something", typo="CharField", name="something_dfield_charfield", verbose_name = u"Dynamic Field Str", html_attrs={'data-mask': 'charfield'})
        DynamicField.objects.create(id=3, refer="Something", typo="Date", name="something_dfield_date", verbose_name = u"Dynamic Field Date", html_attrs={'data-mask': 'date'})
        DynamicField.objects.create(id=4, refer="Something", typo="DateTime", name="something_dfield_datetime", verbose_name=u"Dynamic Field DateTime", html_attrs={'data-mask': 'datetime'})
        DynamicField.objects.create(id=5, refer="Something", typo="Monetary", name="something_dfield_monetary", verbose_name=u"Dynamic Field Decimal", html_attrs={'data-mask': 'monetary'})
        DynamicField.objects.create(id=6, refer="Something", typo="MultSelect", name="something_dfield_multiselect", verbose_name=u"Dynamic Field MultiSelect", choices=['1', '2', '3', '4'], html_attrs={'data-mask': 'multipleselect'})
        DynamicField.objects.create(id=7, refer="Something", typo="RadioButton", name="something_dfield_radiobutton", verbose_name=u"Dynamic Field RadioButton", choices=['1', '2', '3', '4'], html_attrs={'data-mask': 'radiobutton'})
        DynamicField.objects.create(id=8, refer="Something", typo="CheckBox", name="something_dfield_checkbox", verbose_name=u"Dynamic Field CheckBox", choices=['1', '2', '3', '4'], html_attrs={'data-mask': 'checkbox'})
        DynamicField.objects.create(id=9, refer="Something", typo="TextArea", name="something_dfield_textarea", verbose_name=u"Dynamic Field TextArea", html_attrs={'data-mask': 'textarea'})
        DynamicField.objects.create(id=10, refer="Something", typo="Float", name="something_dfield_float", verbose_name=u"Dynamic Field Float", html_attrs={'data-mask': 'float'})
        
        self.something = Something.objects.create(
            something_dfield_integer=42,
            something_dfield_monetary=Decimal(42.5),
            something_dfield_charfield=u"Dynamic Field Str",
            something_dfield_date=date.today(),
            something_dfield_datetime=datetime.now(),
            something_dfield_multiselect=['A', 'B', 'C'],
            something_dfield_radiobutton='2',
            something_dfield_checkbox=['1', '2', '3'],
            something_dfield_textarea="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            something_dfield_float=42.5,
        )
    
    # def test_assert_form_as_p_render(self):
    #     expected = u'<p><label for="id_name">Name:</label> <input id="id_name" type="text" name="name" maxlength="32" /></p>\n<p><label for="id_something_group">Group:</label> <select name="something_group" id="id_something_group">\n<option value="" selected="selected">---------</option>\n</select></p>\n<p><label for="id_something_dfield_integer">Dynamic Field Int:</label> <input data-mask="integer" type="text" name="something_dfield_integer" value="42" id="id_something_dfield_integer" /></p>\n<p><label for="id_something_dfield_charfield">Dynamic Field Str:</label> <input data-mask="charfield" type="text" name="something_dfield_charfield" value="Dynamic Field Str" id="id_something_dfield_charfield" /></p>\n<p><label for="id_something_dfield_date">Dynamic Field Date:</label> <input data-mask="date" type="text" name="something_dfield_date" value="%s" id="id_something_dfield_date" /></p>\n<p><label for="id_something_dfield_datetime">Dynamic Field DateTime:</label> <input data-mask="datetime" type="text" name="something_dfield_datetime" value="%s" id="id_something_dfield_datetime" /></p>\n<p><label for="id_something_dfield_monetary">Dynamic Field Decimal:</label> <input data-mask="monetary" type="text" name="something_dfield_monetary" value="42.5" id="id_something_dfield_monetary" /></p>\n<p><label for="id_something_dfield_multiselect">Dynamic Field MultiSelect:</label> <select multiple="multiple" data-mask="multipleselect" name="something_dfield_multiselect" id="id_something_dfield_multiselect">\n<option value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]">[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</option>\n</select></p>\n<p><label for="id_something_dfield_radiobutton_0">Dynamic Field RadioButton:</label> <ul>\n<li><label for="id_something_dfield_radiobutton_0"><input data-mask="radiobutton" type="radio" id="id_something_dfield_radiobutton_0" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" name="something_dfield_radiobutton" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul></p>\n<p><label for="id_something_dfield_checkbox_0">Dynamic Field CheckBox:</label> <ul>\n<li><label for="id_something_dfield_checkbox_0"><input data-mask="checkbox" type="checkbox" name="something_dfield_checkbox" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" id="id_something_dfield_checkbox_0" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul></p>\n<p><label for="id_something_dfield_textarea">Dynamic Field TextArea:</label> <textarea data-mask="textarea" id="id_something_dfield_textarea" rows="10" cols="40" name="something_dfield_textarea">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</textarea></p>\n<p><label for="id_something_dfield_float">Dynamic Field Float:</label> <input data-mask="float" type="text" name="something_dfield_float" value="42.5" id="id_something_dfield_float" /></p>' % (self.something.something_dfield_date.strftime('%d/%m/%Y'), self.something.something_dfield_datetime.strftime('%d/%m/%Y %H:%M:%S'))
    #     if DJANGO_VERSION >= (1, 5):
    #         expected = u'<p><label for="id_name">Name:</label> <input id="id_name" maxlength="32" name="name" type="text" /></p>\n<p><label for="id_something_group">Group:</label> <select id="id_something_group" name="something_group">\n<option value="" selected="selected">---------</option>\n</select></p>\n<p><label for="id_something_dfield_charfield">Dynamic Field Str:</label> <input data-mask="charfield" id="id_something_dfield_charfield" name="something_dfield_charfield" type="text" value="Dynamic Field Str" /></p>\n<p><label for="id_something_dfield_date">Dynamic Field Date:</label> <input data-mask="date" id="id_something_dfield_date" name="something_dfield_date" type="text" value="%s" /></p>\n<p><label for="id_something_dfield_datetime">Dynamic Field DateTime:</label> <input data-mask="datetime" id="id_something_dfield_datetime" name="something_dfield_datetime" type="text" value="%s" /></p>\n<p><label for="id_something_dfield_monetary">Dynamic Field Decimal:</label> <input data-mask="monetary" id="id_something_dfield_monetary" name="something_dfield_monetary" type="text" value="42.5" /></p>\n<p><label for="id_something_dfield_multiselect">Dynamic Field MultiSelect:</label> <select multiple="multiple" data-mask="multipleselect" id="id_something_dfield_multiselect" name="something_dfield_multiselect">\n<option value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]">[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</option>\n</select></p>\n<p><label for="id_something_dfield_radiobutton_0">Dynamic Field RadioButton:</label> <ul>\n<li><label for="id_something_dfield_radiobutton_0"><input data-mask="radiobutton" id="id_something_dfield_radiobutton_0" name="something_dfield_radiobutton" type="radio" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul></p>\n<p><label for="id_something_dfield_checkbox_0">Dynamic Field CheckBox:</label> <ul>\n<li><label for="id_something_dfield_checkbox_0"><input data-mask="checkbox" id="id_something_dfield_checkbox_0" name="something_dfield_checkbox" type="checkbox" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul></p>\n<p><label for="id_something_dfield_textarea">Dynamic Field TextArea:</label> <textarea cols="40" data-mask="textarea" id="id_something_dfield_textarea" name="something_dfield_textarea" rows="10">\r\nLorem ipsum dolor sit amet, consectetur adipiscing elit.</textarea></p>\n<p><label for="id_something_dfield_float">Dynamic Field Float:</label> <input data-mask="float" id="id_something_dfield_float" name="something_dfield_float" type="text" value="42.5" /></p>\n<p><label for="id_something_dfield_integer">Dynamic Field Int:</label> <input data-mask="integer" id="id_something_dfield_integer" name="something_dfield_integer" type="text" value="42" /></p>' % (self.something.something_dfield_date.strftime('%d/%m/%Y'), self.something.something_dfield_datetime.strftime('%d/%m/%Y %H:%M:%S'))
    #     self.assertEqual(
    #         SomethingForm(instance=self.something).as_p(),
    #         expected
    #     )

    def test_assert_integer_render(self):
        expected = u'<input data-mask="integer" type="text" name="something_dfield_integer" value="%s" />' % self.something.something_dfield_integer
        if DJANGO_VERSION >= (1, 5):
            expected = u'<input data-mask="integer" name="something_dfield_integer" type="text" value="%s" />' % self.something.something_dfield_integer
            
        self.assertEqual(
            SomethingForm().fields['something_dfield_integer'].widget.render('something_dfield_integer', self.something.something_dfield_integer),
            expected
        )

    def test_assert_charfield_render(self):
        expected = u'<input data-mask="charfield" type="text" name="something_dfield_charfield" value="%s" />' % self.something.something_dfield_charfield
        if DJANGO_VERSION >= (1, 5):
            expected = u'<input data-mask="charfield" name="something_dfield_charfield" type="text" value="%s" />' % self.something.something_dfield_charfield
        self.assertEqual(
            SomethingForm().fields['something_dfield_charfield'].widget.render('something_dfield_charfield', self.something.something_dfield_charfield),
            expected
        )

    def test_assert_date_render(self):
        expected = u'<input data-mask="date" type="text" name="something_dfield_date" value="%s" />' % self.something.something_dfield_date.strftime('%d/%m/%Y')
        if DJANGO_VERSION >= (1, 5):
            expected = u'<input data-mask="date" name="something_dfield_date" type="text" value="%s" />' % self.something.something_dfield_date.strftime('%d/%m/%Y')
        self.assertEqual(
            SomethingForm().fields['something_dfield_date'].widget.render('something_dfield_date', self.something.something_dfield_date),
            expected
        )

    def test_assert_datetime_render(self):
        expected = u'<input data-mask="datetime" type="text" name="something_dfield_datetime" value="%s" />' % self.something.something_dfield_datetime.strftime('%d/%m/%Y %H:%M:%S')
        if DJANGO_VERSION >= (1, 5):
            expected = u'<input data-mask="datetime" name="something_dfield_datetime" type="text" value="%s" />' % self.something.something_dfield_datetime.strftime('%d/%m/%Y %H:%M:%S')
        self.assertEqual(
            SomethingForm().fields['something_dfield_datetime'].widget.render('something_dfield_datetime', self.something.something_dfield_datetime),
            expected
        )

    def test_assert_monetary_render(self):
        expected = u'<input data-mask="monetary" type="text" name="something_dfield_monetary" value="42.5" />'
        if DJANGO_VERSION >= (1, 5):
            expected = u'<input data-mask="monetary" name="something_dfield_monetary" type="text" value="42.5" />'
        self.assertEqual(
            SomethingForm().fields['something_dfield_monetary'].widget.render('something_dfield_monetary', self.something.something_dfield_monetary),
            expected
        )

    def test_assert_multselect_render(self):
        expected = u'<select multiple="multiple" data-mask="multipleselect" name="something_dfield_multiselect">\n<option value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]">[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</option>\n</select>'
        if DJANGO_VERSION >= (1, 5):
            expected = u'<select multiple="multiple" data-mask="multipleselect" name="something_dfield_multiselect">\n<option value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]">[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</option>\n</select>'
        self.assertEqual(
            SomethingForm().fields['something_dfield_multiselect'].widget.render('something_dfield_multiselect', self.something.something_dfield_multiselect),
            expected
        )

    def test_assert_radiobutton_render(self):
        expected = u'<ul>\n<li><label><input data-mask="radiobutton" type="radio" name="something_dfield_radiobutton" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul>'
        if DJANGO_VERSION >= (1, 5):
            expected = u'<ul>\n<li><label><input data-mask="radiobutton" name="something_dfield_radiobutton" type="radio" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul>'
        self.assertEqual(
            SomethingForm().fields['something_dfield_radiobutton'].widget.render('something_dfield_radiobutton', self.something.something_dfield_radiobutton),
            expected
        )

    def test_assert_checkbox_render(self):
        expected = u'<ul>\n<li><label><input data-mask="checkbox" type="checkbox" name="something_dfield_checkbox" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul>'
        if DJANGO_VERSION >= (1, 5):
            expected = u'<ul>\n<li><label><input data-mask="checkbox" name="something_dfield_checkbox" type="checkbox" value="[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]" /> [&#39;1&#39;, &#39;2&#39;, &#39;3&#39;, &#39;4&#39;]</label></li>\n</ul>'
        self.assertEqual(
            SomethingForm().fields['something_dfield_checkbox'].widget.render('something_dfield_checkbox', self.something.something_dfield_checkbox),
            expected
        )

    def test_assert_textarea_render(self):
        expected = u'<textarea data-mask="textarea" rows="10" cols="40" name="something_dfield_textarea">[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;]</textarea>'
        if DJANGO_VERSION >= (1, 5):
            expected = u'<textarea cols="40" data-mask="textarea" name="something_dfield_textarea" rows="10">\r\n[&#39;1&#39;, &#39;2&#39;, &#39;3&#39;]</textarea>'

        self.assertEqual(
            SomethingForm().fields['something_dfield_textarea'].widget.render('something_dfield_textarea', self.something.something_dfield_checkbox),
            expected
        )

    def test_assert_float_render(self):
        expected = u'<input data-mask="float" type="text" name="something_dfield_float" value="%s" />' % self.something.something_dfield_float
        if DJANGO_VERSION >= (1, 5):
            expected = u'<input data-mask="float" name="something_dfield_float" type="text" value="%s" />' % self.something.something_dfield_float
            
        self.assertEqual(
            SomethingForm().fields['something_dfield_float'].widget.render('something_dfield_float', self.something.something_dfield_float),
            expected
        )

    