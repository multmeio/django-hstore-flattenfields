from django import VERSION
from django.db.models import get_app
from django.test.simple import DjangoTestSuiteRunner
from django.test import _doctest as doctest

if VERSION[:2] >= (1, 6):
    from django.test._doctest import DocTestRunner
else:
    from django.test.testcases import DocTestRunner

import re
import os
import imp

EXCLUDE_FILES = ['__init__.py', 'tests.py', 'models.py']

def is_testable(filename):
    return filename.endswith(".py") and \
           filename not in EXCLUDE_FILES

def pretty_pkgs(pkgs):
    return map(
        lambda x: re.sub('\.py$', '', x), 
        filter(is_testable, pkgs)
    )

def find_modules(package):
    for pkg in os.walk(os.path.dirname(package.__file__)):
        for file in pretty_pkgs(pkg[2]):
            try:
                yield imp.load_module(
                    file, *imp.find_module(file, [pkg[0]])
                )
            except:
                continue
    
class DjangoWithDoctestTestRunner(DjangoTestSuiteRunner):
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        old_suite = super(DjangoWithDoctestTestRunner, self).build_suite(
            test_labels, extra_tests, **kwargs
        )
        for label in test_labels:
            parts = label.split('.')
            for module in find_modules(get_app(parts[0])):
                try:
                    test_obj = doctest.DocTestSuite(
                        module, runner=DocTestRunner
                    )
                except ValueError:
                    continue
                else:
                    old_suite.addTest(test_obj)
        return old_suite
