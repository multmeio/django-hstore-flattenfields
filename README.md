Django-hstore-flattenfields
===========================
---
Django-hstore-flattenfields is an alternative for who want to have a Dynamic Scheme in Django without rely on a NoSQL database. Django-hstore-flattenfields add "dynamic fields" in Django Models, using the [Hstore](http://www.postgresql.org/docs/9.1/static/hstore.html) extension built in the PostgreSQL v9.1+. This way you can quickly add new fields in a Model, with some great features.

*Django-hstore-flattenfields is built and used in the [Multmeio](http://www.multmeio.com.br) enterprise.*

Status:

![Downloads](https://pypip.in/d/django_hstore_flattenfields/badge.png)

CIBuildStatus

![Codeship Status for multmeio/django-hstore-flattenfields](https://www.codeship.io/projects/7179a640-f087-0130-5d53-7e0d6fca55d7/status?branch=content_pane_and_dynamic_field_group)

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

*TODO Add usage information and useful example*


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
