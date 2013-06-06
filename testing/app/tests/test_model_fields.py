from django.test import TestCase
from decimal import Decimal

from hstore_flattenfields.fields import *
from hstore_flattenfields.models import DynamicField

from app.models import Something


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
        self.assertEqual(f._format(f.to_python(2)), '2.0')
        self.assertEqual(f._format(f.to_python('2.6')), '2.6')
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
        def _update_something(obj, value):
            obj.something_dfield_int = value;
            obj.save()

        f = HstoreIntegerField(name='something_dfield_int')
        DynamicField.objects.create(id=1, refer="Something", typo="Integer", name="something_dfield_int", verbose_name = u"Dynamic Field Int")
        something = Something.objects.create(something_dfield_int=3)

        self.assertEqual(f.value_to_string(something), 3)
        _update_something(something, -3)
        self.assertEqual(f.value_to_string(something), -3)
        _update_something(something, None)
        self.assertEqual(f.value_to_string(something), None)
        _update_something(something, 'aaa')
        self.assertEqual(f.value_to_string(something), None)

