# encoding: utf-8
import os
from setuptools import setup, find_packages

setup(
    name='django_hstore_flattenfields',
    version=__import__('hstore_flattenfields').__version__,
    description='Django with dynamic fields in hstore',
    author=u'Iuri Diniz',
    author_email='iuridiniz@gmail.com',
    maintainer=u'Luís Araújo',
    maintainer_email='caitifbrito@gmail.com',
    url='https://github.com/multmeio/django-hstore-flattenfields',
    packages=find_packages(exclude=['example', 'example.*']),
    # long_description=read('README.rst'),
    test_suite='runtests.runtests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=[
        'django>=1.4',
        'django-bootstrap-toolkit==2.5.4',
        'django-orm-extensions==3.0b3',
        'django-extensions>=0.9',
        'django-cache-machine>=0.6'
    ]
)
