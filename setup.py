# encoding: utf-8
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django_hstore_flattenfields',
    version='0.7.1',
    description='Django with dynamic fields in hstore',
    author=u'Iuri Diniz',
    author_email='iuridiniz@gmail.com',
    maintainer=u'Luís Araújo',
    maintainer_email='caitifbrito@gmail.com',
    url='https://github.com/multmeio/django-hstore-flattenfields',
    packages=find_packages(
        exclude=['example', 'example.*']),
    # long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
    install_requires=['Django',
    	'django-orm-extensions']
)
