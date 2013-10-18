Django-hstore-flattenfields
===========================
[![PyPi version](https://pypip.in/v/django_hstore_flattenfields/badge.png)](https://pypi.python.org/pypi/django_hstore_flattenfields/)
[![Downloads](https://pypip.in/d/django_hstore_flattenfields/badge.png)](https://crate.io/packages/django_hstore_flattenfields/)
[![Coverage Status](https://coveralls.io/repos/multmeio/django-hstore-flattenfields/badge.png?branch=master)](https://coveralls.io/r/multmeio/django-hstore-flattenfields?branch=master)
[![Build Status](https://travis-ci.org/multmeio/django-hstore-flattenfields.png?branch=master)](https://travis-ci.org/multmeio/django-hstore-flattenfields)

Django-hstore-flattenfields is an alternative for who want to have a Dynamic Scheme in Django without rely on a NoSQL database. Django-hstore-flattenfields add "dynamic fields" in Django Models, using the [Hstore](http://www.postgresql.org/docs/9.1/static/hstore.html) extension built in the PostgreSQL v9.1+. This way you can quickly add new fields in a Model, with some great features.

*Django-hstore-flattenfields is built and used in the [Multmeio](http://www.multmeio.com.br) enterprise.*

#### Some great features are:
* ModelForms
* *.objects.create()
* Automatic type parsing
* QuerySet filters (exact, iexact, contains, icontains, startswith, istartswith, endswith, iendswith, in, lt, lte, gt, gte)
* Aggregations


Install and usage
-----------------

#### Installation
Install django-hstore-flattenfields with pip:

```sh
$ pip install django-hstore-flattenfields
```

You're done! django-hstore-flattenfields is ready to use! ;)

#### Usage and example

For a full example click [here](https://github.com/multmeio/django-hstore-flattenfields/tree/master/example).

Diagram Application

![diagram](https://raw.github.com/multmeio/django-hstore-flattenfields/master/doc/application_diagram.png)

Development
------------

Star and follow us!

Fork and clone this repository.

```sh
$ git clone git@github.com:<username>/django-hstore-flattenfields.git
```

 *Change \<username\> to your GitHub account.*

Cd into django-hstore-flattenfields directory and install it's dependencies:

```sh
$ cd django-hstore-flattenfields/
$ pip install -r requirements.txt
```

Now start pushing! :D


Help
--------

Read our [documentation](http://django-hstore-flattenfields.readthedocs.org).
*TODO Add contact/help options*
