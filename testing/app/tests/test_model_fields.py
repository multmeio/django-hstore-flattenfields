from django.test import TestCase
from decimal import Decimal

from hstore_flattenfields.fields import HstoreDecimalField

class DecimalFieldTests(TestCase):
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
