from django.db.models import get_app
from django.test.simple import DjangoTestSuiteRunner
from django.test.testcases import DocTestRunner
from django.test import _doctest as doctest

import re
import os
import imp

EXCLUDE_FILES = ['__init__.py', 'tests.py', 'models.py']

def is_testable(filename):
    return filename.endswith(".py") and filename not in EXCLUDE_FILES

def find_modules(package):
    pkg_files = [(p,f) for p,d,f in os.walk(os.path.dirname(package.__file__)) \
                 if len(d) > 0 and not d[0] == "tests"]
    loaded_modules = []
    for pkg in pkg_files:
        loaded_modules.extend(
            [imp.load_module(file, *imp.find_module(file, [pkg[0]])) \
            for file in map(lambda x: re.sub('\.py$', '', x), 
                filter(is_testable, pkg[1])
            )]
        )
    return loaded_modules
    
class DjangoWithDoctestTestRunner(DjangoTestSuiteRunner):
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        old_suite = super(DjangoWithDoctestTestRunner, self).build_suite(
            test_labels, extra_tests, **kwargs
        )
        for label in test_labels:
            parts = label.split('.')
            for module in find_modules(get_app(parts[0])):
                old_suite.addTest(
                    doctest.DocTestSuite(module, runner=DocTestRunner)
                )
        return old_suite
