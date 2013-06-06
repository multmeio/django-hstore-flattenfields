from django.test import TestCase
from decimal import Decimal
from datetime import date, datetime

from hstore_flattenfields.fields import *
from hstore_flattenfields.models import DynamicField

from app.models import Something

def _update_obj(obj, field, value):
    setattr(obj, field, value); obj.save()

class HstoreDecimalFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreDecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal("3"))
        self.assertEqual(f.to_python("3.14"), Decimal("3.14"))
        self.assertEqual(f.to_python("abc"), "")

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


class HstoreDateFieldTests(TestCase):
    def test_to_python(self):
        f = HstoreDateField()
        self.assertEqual(f.to_python("2013-05-25"), date(2013, 05, 25))
        self.assertEqual(f.to_python("2013-52-99"), "")
        self.assertEqual(f.to_python(None), "")

    def test_value_to_string(self):
        f = HstoreDateField(name="something_dfield_date")
        DynamicField.objects.create(id=1, refer="Something", typo="Date", name="something_dfield_date", verbose_name=u"Dynamic Field Date")
        something = Something.objects.create(something_dfield_date="2013-05-25")

        self.assertEqual(f.value_to_string(something), "2013-05-25")
        _update_obj(something, "something_dfield_date", "2013-52-99")
        self.assertEqual(f.value_to_string(something), "")
        _update_obj(something, "something_dfield_date", None)
        self.assertEqual(f.value_to_string(something), "")
