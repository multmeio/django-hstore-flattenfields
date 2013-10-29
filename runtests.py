#!/usr/bin/env python

import os
import sys
import optparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

def parse_args():
    parser = optparse.OptionParser()
    args = parser.parse_args()[1]
    
    # NOTE: When the test mode is called from setup.py
    try:
        args.remove('test')
    except ValueError:
        pass
    
    return args or ['app', 'hstore_flattenfields']


def configure_settings():
    from django.conf import settings
    return settings


def get_runner(settings):
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests():
    test_labels = parse_args()
    settings = configure_settings()
    runner = get_runner(settings)
    sys.exit(runner.run_tests(test_labels))


if __name__ == '__main__':
    runtests()
