from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime
from django.db.models.fields import NOT_PROVIDED

from hstore_flattenfields.db.fields import *
from hstore_flattenfields.models import DynamicField

from tests.app.models import *


def _update_obj(obj, field, value):
    setattr(obj, field, value); obj.save()


class HstoreTextFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreTextField()
        self.assertEqual(f.to_python(3), '3')
        self.assertEqual(f.to_python("3"), '3')
        self.assertEqual(f.to_python(NOT_PROVIDED), None)
        self.assertEqual(f.to_python("abc"), 'abc')


class HstoreCharFieldTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(
            refer="Author", typo="Input", 
            name="author_choices", verbose_name=u"Author Choices", 
            choices=['1', '2', '3', '4']
        )
        DynamicField.objects.create(
            refer="Author", typo="Input", 
            name="author_broken_choices", 
            verbose_name=u"Author Broken Choices"
        )

    def test_get_choices(self):
        choices = HstoreCharField(name="author_choices")
        self.assertEqual(
            choices.get_choices(), 
            [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')]
        )
        self.assertEqual(
            choices.get_choices(include_blank=True), 
            [('', '----'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')]
        )
        broken_choices = HstoreCharField(name="author_broken_choices")
        self.assertEqual(
            broken_choices.get_choices(), 
            []
        )
        self.assertEqual(
            broken_choices.get_choices(include_blank=True), 
            []
        )

    def test_to_python(self):
        f = HstoreCharField()
        self.assertEqual(f.to_python(3), '3')
        self.assertEqual(f.to_python("3"), '3')
        self.assertEqual(f.to_python(NOT_PROVIDED), None)
        self.assertEqual(f.to_python("abc"), 'abc')

        

class HstoreDecimalFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreDecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal("3"))
        self.assertEqual(f.to_python("3.14"), Decimal("3.14"))
        self.assertEqual(f.to_python("abc"), None)
        self.assertEqual(f.to_python(NOT_PROVIDED), None)

    def test_default(self):
        f = HstoreDecimalField(default=Decimal("0.00"))
        self.assertEqual(f.get_default(), Decimal("0.00"))

    def test_format(self):
        f = HstoreDecimalField(max_digits=5, decimal_places=1)
        self.assertEqual(f._format(f.to_python(2)), "2.0")
        self.assertEqual(f._format(f.to_python("2.6")), "2.6")
        self.assertEqual(f._format(None), None)


class HstoreIntegerFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreIntegerField()
        self.assertEqual(f.to_python(3), 3)
        self.assertEqual(f.to_python("3"), 3)
        self.assertEqual(f.to_python("3.14"), None)
        self.assertEqual(f.to_python("abc"), None)

    def test_default(self):
        f = HstoreIntegerField(default=0)
        self.assertEqual(f.get_default(), 0)

    def test_value_to_string(self):
        f = HstoreIntegerField(name="something_dfield_int")
        DynamicField.objects.create(id=1, refer="Something", typo="Integer", name="something_dfield_int", verbose_name=u"Dynamic Field Int")
        something = Something.objects.create(something_dfield_int=3)

        self.assertEqual(f.value_to_string(something), 3)
        _update_obj(something, "something_dfield_int", -3)
        self.assertEqual(f.value_to_string(something), -3)
        _update_obj(something, "something_dfield_int", None)
        self.assertEqual(f.value_to_string(something), None)
        _update_obj(something, "something_dfield_int", "aaa")
        self.assertEqual(f.value_to_string(something), None)

    def test_clean(self):
        f = HstoreIntegerField(name="something_dfield_int")
        self.assertEqual(
            f.clean(42, Something()),
            42
        )


class HstoreDateFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreDateField()
        self.assertEqual(f.to_python("2013-05-25"), date(2013, 05, 25))
        self.assertRaises(ValueError, f.to_python, "2013-52-99")
        self.assertEqual(f.to_python(None), None)

    def test_value_to_string(self):
        f = HstoreDateField(name="something_dfield_date")
        DynamicField.objects.create(id=1, refer="Something", typo="Date", name="something_dfield_date", verbose_name=u"Dynamic Field Date")
        something = Something.objects.create(something_dfield_date="2013-05-25")

        self.assertEqual(f.value_to_string(something), "2013-05-25")
        with self.assertRaises(ValueError):
            _update_obj(something, "something_dfield_date", "2013-52-99")
            self.assertEqual(f.value_to_string(something), "")
        _update_obj(something, "something_dfield_date", None)
        self.assertEqual(f.value_to_string(something), "")

    def test_clean(self):
        f = HstoreDateField(name="something_dfield_date")
        self.assertEqual(
            f.clean(date(2013, 05, 25), Something()),
            date(2013, 05, 25)
        )


class HstoreDateFieldBrTests(TestCase):
    def test_to_python(self):
        f = HstoreDateField()
        self.assertEqual(f.to_python("25/05/2013"), date(2013, 05, 25))
        self.assertRaises(ValueError, f.to_python, "99/52/2013")
        self.assertEqual(f.to_python(None), None)

    def test_value_to_string(self):
        f = HstoreDateField(name="something_dfield_date")
        DynamicField.objects.create(id=1, refer="Something", typo="Date", name="something_dfield_date", verbose_name=u"Dynamic Field Date")
        something = Something.objects.create(something_dfield_date="25/05/2013")

        self.assertEqual(f.value_to_string(something), "2013-05-25")
        with self.assertRaises(ValueError):
            _update_obj(something, "something_dfield_date", "99/52/2013")
            self.assertEqual(f.value_to_string(something), "")
        _update_obj(something, "something_dfield_date", None)
        self.assertEqual(f.value_to_string(something), "")


class HstoreDateTimeFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreDateTimeField()
        self.assertEqual(f.to_python("2013-06-03 11:04:05"), datetime(2013, 6, 3, 11, 4, 5))
        self.assertRaises(ValidationError, f.to_python, "2013-52-99 131:04:5")
        self.assertEqual(f.to_python(None), None)

    def test_value_to_string(self):
        f = HstoreDateTimeField(name="something_dfield_datetime")
        DynamicField.objects.create(id=1, refer="Something", typo="DateTime", name="something_dfield_datetime", verbose_name=u"Dynamic Field Datetime")
        something = Something.objects.create(something_dfield_datetime="2013-05-25 11:04:33")

        self.assertEqual(f.value_to_string(something), "2013-05-25T11:04:33")
        _update_obj(something, "something_dfield_datetime", datetime(2013, 2, 9, 11, 30, 22))

        self.assertEqual(f.value_to_string(something), "2013-02-09T11:30:22")
        _update_obj(something, "something_dfield_datetime", None)
        self.assertEqual(f.value_to_string(something), "")

    def test_clean(self):
        f = HstoreDateTimeField(name="something_dfield_datetime")
        self.assertEqual(
            f.clean(datetime(2013, 2, 9, 11, 30, 22), Something()),
            datetime(2013, 2, 9, 11, 30, 22)
        )

class HstoreRadioSelectFieldTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(
            refer="Something", typo="RadioButton", 
            name="something_dfield_radioselect", 
            verbose_name=u"Dynamic Field Radio Select",
            choices=['1', '2', '3', '4']
        )

    def test_default(self):
        f = HstoreRadioSelectField(name="something_dfield_radioselect", default='2', choices=['1', '2', '3', '4'])
        self.assertEqual(f.default, '2')
        self.assertEqual(f.get_default(), '2')

    def test_format(self):
        f = HstoreRadioSelectField(name="something_dfield_radioselect", choices=['1', '2', '3', '4'])
        self.assertEqual(f.to_python("['2']"), "['2']")
        self.assertEqual(f.to_python(['2']), ['2'])
        self.assertEqual(f.to_python(['1', '2']), ['1', '2'])
        self.assertEqual(f.to_python([]), [])
        self.assertEqual(f.to_python(None), None)

    def test_choices(self):
        f = HstoreRadioSelectField(name="something_dfield_radioselect", choices=['1', '2', '3', '4'])
        self.assertEqual(
            f.get_choices(), 
            [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')]
        )
        self.assertEqual(
            f.get_choices(include_blank=True), 
            [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')]
        )


class HstoreCheckboxFieldTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(
            refer="Something", typo="CheckBox", 
            name="something_dfield_checkbox", 
            verbose_name=u"Dynamic Field Radio Select",
            choices=['1', '2', '3', '4']
        )

    def test_default(self):
        f = HstoreCheckboxField(name="something_dfield_checkbox", default='1', choices=['1', '2', '3', '4'])
        self.assertEqual(f.get_default(), '1')

    def test_format(self):
        f = HstoreCheckboxField(name="something_dfield_checkbox", choices=['1', '2', '3', '4'])
        self.assertEqual(f.to_python(['2']), ['2'])
        self.assertEqual(f.to_python(['1', '2']), ['1', '2'])
        self.assertEqual(f.to_python([]), [])
        self.assertEqual(f.to_python(None), [])

    def test_choices(self):
        f = HstoreCheckboxField(name="something_dfield_checkbox", choices=['1', '2', '3', '4'])
        self.assertEqual(f.get_choices(), [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])

    def test_clean(self):
        f = HstoreCheckboxField(name="something_dfield_checkbox", choices=['1', '2', '3', '4'])
        self.assertEqual(
            f.clean("1", Something()),
            "1"
        )


class HstoreSelectFieldTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(
            refer="Something", typo="SelectBox", 
            name="something_select_multiple", 
            verbose_name=u"Dynamic Field MultiSelect", 
            choices=['1', '2', '3', '4'],
            blank=True
        )

    def test_format(self):
        f = HstoreSelectField(name="something_select_multiple", choices=['1', '2', '3', '4'])
        self.assertEqual(f.to_python(9999), 9999)
        self.assertEqual(f.to_python(None), None)
        self.assertEqual(f.to_python(NOT_PROVIDED), None)

    def test_choices(self):
        f = HstoreSelectField(name="something_select_multiple", choices=['1', '2', '3', '4'])
        self.assertEqual(
            f.get_choices(), 
            ['1', '2', '3', '4']
        )


class HstoreMultipleSelectFieldTests(TestCase):
    def setUp(self):
        DynamicField.objects.create(
            refer="Something", typo="MultSelect", 
            name="something_select_multiple", 
            verbose_name=u"Dynamic Field MultiSelect", 
            choices=['1', '2', '3', '4'],
            blank=True
        )

    def test_format(self):
        f = HstoreMultipleSelectField(name="something_select_multiple", choices=['1', '2', '3', '4'])
        self.assertEqual(f.to_python(9999), [])
        self.assertEqual(f.to_python(['2']), ['2'])
        self.assertEqual(f.to_python(['1', '2']), ['1', '2'])
        self.assertEqual(f.to_python([]), [])
        self.assertEqual(f.to_python(None), [])

    def test_choices(self):
        f = HstoreMultipleSelectField(name="something_select_multiple", choices=['1', '2', '3', '4'])
        self.assertEqual(f.get_choices(), [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])
        self.assertEqual(
            f.get_choices(include_blank=True), 
            [('', '----'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')]
        )

    def test_clean(self):
        f = HstoreMultipleSelectField(name="something_select_multiple", choices=['1', '2', '3', '4'])
        self.assertEqual(
            f.clean(["1", "2"], Something()),
            ["1", "2"]
        )

