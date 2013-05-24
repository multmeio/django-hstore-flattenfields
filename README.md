django-hstore-flattenfields
===============
-----------
This project is an alternative for who want to have a Dynamic Scheme in Django, we have the goal to add 'dynamic fields' in the Django Models, we use the Hstore extension built in the PostgreSQL V9.1+, using this you can quickly add new fields in a Model, with some great features, he is built and used in the [Multmeio](http://www.multmeio.com.br) enterprise.


DynamicFields are suportated:
* ModelForms
* *.objects.create() method, accept the DynamicFields.
* QuerySet (Simple Filters and Exclude)
   * ['exact', 'iexact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith', 'in', 'lt', 'lte', 'gt', 'gte']
* Parse types
   * If your DynamicField was a DateTimeField, when the Flattenfields will save he will convert your data in DateTimeField automatically.

How to install e config
===============
-----------
#### Follow the steps:

1. Star this and Follow us;
2. Clone or Download this repo;
3. Install [pip](http://www.pip-installer.org/en/latest/) or [easy_install](http://pythonhosted.org/distribute/easy_install.html);
4. Install the project dependencies;
    - ```pip install -r requirements.txt``` in your root project folder.
5. Setup the ```DATABASES``` confs, inside the [settings](https://github.com/multmeio/django-hstore-flattenfields/blob/master/example/hstoredyn/settings.py#L12) file.
6. Sync your database with the project models and external apps's models:
    - ```python manage.py syncdb```
7. Migrate your database's  schema, use the South's command called **migrate**
    - ```python manage.py migrate```
8. Run the tests.
    - ```python manage.py test app```
9. Run your project:
    - ```python manage.py runserver```
10. See in the localhost;
    - ```127.0.0.1:8000```

- You can change the *port* what django will run your project:
    - ```python manage.py runserver 8080``` --> ```127.0.0.1:8080```
