#!/usr/bin/env python
# encoding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from models import *
from hstore_flattenfields.models import DynamicField

DICT_SOMETHING = dict(
    name = u"Some Name"
)

DICT_SOMETHING_DYNAMIC_FIELD = dict(
    refer="Something",
    name="something_custom_attribute",
    verbose_name = u"Something Attribute",
    typo="CharField",
)

DICT_DFIELD_INT = dict(
    id=1,
    refer="Something",
    typo="Integer",
    name="something_dfield_int",
    verbose_name = u"Dynamic Field Int",
)

DICT_DFIELD_STR = dict(
    id=2,
    refer="Something",
    typo="CharField",
    name="something_dfield_str",
    verbose_name = u"Dynamic Field Str",
)

LIST_DFIELD_INT_VALUES = [
    {'something_dfield_int': u''},
    {'something_dfield_int': u'41'},
    {'something_dfield_int': u''},
    {'something_dfield_int': u'39'},
    {'something_dfield_int': u''},
    {'something_dfield_int': u'37'},
    {'something_dfield_int': u''},
    {'something_dfield_int': u'35'},
    {'something_dfield_int': u''},
    {'something_dfield_int': u'33'}
]

LIST_DFIELD_INT_VALUES_LIST =  [(u'',), (u'41',), (u'',), (u'39',), (u'',),
                                (u'37',), (u'',), (u'35',), (u'',), (u'33',)]

LIST_DFIELD_INT_VALUES_LIST_FLAT = [u'', u'41', u'', u'39', u'',
                                    u'37', u'', u'35', u'', u'33']


LIST_DFIELD_STR_VALUES = [{'something_dfield_str': u''}, {'something_dfield_str': u'41'}, {'something_dfield_str': u''}, {'something_dfield_str': u'39'}, {'something_dfield_str': u''}, {'something_dfield_str': u'37'}, {'something_dfield_str': u''}, {'something_dfield_str': u'35'}, {'something_dfield_str': u''}, {'something_dfield_str': u'33'}]

LIST_DFIELD_STR_VALUES_LIST = [(u'',), (u'41',), (u'',), (u'39',), (u'',),
                          (u'37',), (u'',), (u'35',), (u'',), (u'33',)]

LIST_DFIELD_STR_VALUES_LIST_FLAT = [u'', u'41', u'', u'39', u'', u'37',
                                    u'', u'35', u'', u'33']

class TestSomething(TestCase):
    def setUp(self):
        self.dict_something = DICT_SOMETHING.copy()
        self.dict_something.update({
            'something_custom_attribute': "Custom Attribute"
        })
        DynamicField.objects.create(**DICT_SOMETHING_DYNAMIC_FIELD)

    def test_creation_w_dynamic_field(self):
        something = Something.objects.create(**self.dict_something)
        self.assertEqual(
            something.something_custom_attribute,
            "Custom Attribute"
        )

    def test_dynamic_field_edit(self):
        something = Something.objects.create(**self.dict_something)
        self.assertEqual(
            something.something_custom_attribute,
            "Custom Attribute"
        )

        something.something_custom_attribute = "Another Attribute"
        something.save()

        self.assertEqual(
            something.something_custom_attribute,
            "Another Attribute"
        )

class TestSomethingQuerySet(TestCase):
    def setUp(self):
        self.dict_something = DICT_SOMETHING.copy()
        self.something_dfield_str = DynamicField.objects.create(
            **DICT_DFIELD_STR
        )
        self.something_dfield_int = DynamicField.objects.create(
            **DICT_DFIELD_INT
        )

    def test_filter_int(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_int=42
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_int_gt(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 + x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_int__gt=42
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_int_gte(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 + x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_int__gte=42
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_int_lt(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_int__lt=42
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_int_lte(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_int__lte=42
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_int_values(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings_values = [x for x in Something.objects.values('something_dfield_int')]
        self.assertListEqual(somethings_values, LIST_DFIELD_INT_VALUES)

    def test_filter_int_values_list(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings_values_list = [x for x in Something.objects.values_list('something_dfield_int')]
        self.assertListEqual(somethings_values_list, LIST_DFIELD_INT_VALUES_LIST)

    def test_filter_int_values_list_flat(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_int': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings_values_list_flat = [x for x in Something.objects.values_list('something_dfield_int', flat=True)]
        self.assertListEqual(somethings_values_list_flat, LIST_DFIELD_INT_VALUES_LIST_FLAT)

    # +---------------------+
    # |    TEST TO FIXED!   |
    # +---------------------+
    # def test_filter_int_range(self):
    #     for x in xrange(0, 10):
    #         self.dict_something.update({
    #             'something_dfield_int': str(42 - x if x % 2 else "")
    #         })
    #         Something.objects.create(**self.dict_something)
    #     somethings = Something.objects.filter(
    #         something_dfield_int__range=[30, 50]
    #     )
    #     self.assertEqual(somethings.count(), 5)

    def test_filter_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str="so long x3"
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_iexact_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__iexact="so long x3".upper()
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_contains_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__contains="so long"
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_icontains_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__icontains="so long".upper()
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_startswith_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__startswith="so long"
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_istartswith_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__istartswith="so long".upper()
        )
        self.assertEqual(somethings.count(), 5)


    def test_filter_endswith_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__endswith="long x3"
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_iendswith_str(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str("so long x3" if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings = Something.objects.filter(
            something_dfield_str__iendswith="long x3".upper()
        )
        self.assertEqual(somethings.count(), 5)

    def test_filter_str_values(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings_values = [x for x in Something.objects.values('something_dfield_str')]
        self.assertListEqual(somethings_values, LIST_DFIELD_STR_VALUES)

    def test_filter_str_values_list(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings_values_list = [x for x in Something.objects.values_list('something_dfield_str')]
        self.assertListEqual(somethings_values_list, LIST_DFIELD_STR_VALUES_LIST)

    def test_filter_str_values_list_flat(self):
        for x in xrange(0, 10):
            self.dict_something.update({
                'something_dfield_str': str(42 - x if x % 2 else "")
            })
            Something.objects.create(**self.dict_something)
        somethings_values_list_flat = [x for x in Something.objects.values_list('something_dfield_str', flat=True)]
        self.assertListEqual(somethings_values_list_flat, LIST_DFIELD_STR_VALUES_LIST_FLAT)
