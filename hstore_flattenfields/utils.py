#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Luís Antônio Araújo Brito on 2012-10-16.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""

from django.template.defaultfilters import slugify, floatformat
from django.db import connection
from ast import literal_eval
from datetime import datetime

__all__ = ['single_list_to_tuple',
           'str2literal',
           'dec2real',
           'has_any_in',
           'dynamic_field_table_exists',
           'str2date',
           'str2datetime',
           'force_create_table',
]


def single_list_to_tuple(list_values):
    return [(v, v) for v in list_values]

def str2literal(string):
    try:
        return literal_eval(string)
    except:
        return ''

def dec2real(value):
    return floatformat(value, 2)

def str2datetime(value, format="%Y-%m-%d %H:%M:%S.%f"):
    try:
        return datetime.strptime(
            value, format
        )
    except:
        return ''

def str2date(value):
    try:
        return str2datetime(value, "%Y-%m-%d").date()
    except:
        return ''

def has_any_in(chances, possibilities):
    return any([x for x in chances if x in possibilities])

# cache in globals
_DYNAMIC_FIELD_TABLE_EXISTS = None
def dynamic_field_table_exists():
    # NOTE: Error may happen on syncdb, because DynamicField's table does not exist.
    global _DYNAMIC_FIELD_TABLE_EXISTS
    if _DYNAMIC_FIELD_TABLE_EXISTS == None:
      _DYNAMIC_FIELD_TABLE_EXISTS = 'dynamic_field' in connection.introspection.table_names()
    return _DYNAMIC_FIELD_TABLE_EXISTS


def force_create_table():
    cursor = connection.cursor()
    cursor.execute("""
        -- Table: dynamic_field

        -- DROP TABLE dynamic_field;

        CREATE TABLE dynamic_field
        (
          id serial NOT NULL,
          refer character varying(120) NOT NULL,
          name character varying(120) NOT NULL,
          verbose_name character varying(120) NOT NULL,
          typo character varying(20) NOT NULL,
          max_length integer,
          "order" integer,
          blank boolean NOT NULL,
          choices text,
          default_value character varying(80),
          CONSTRAINT dynamic_field_pkey PRIMARY KEY (id),
          CONSTRAINT dynamic_field_name_key UNIQUE (name)
        )
        WITH (
          OIDS=FALSE
        );
        ALTER TABLE dynamic_field
          OWNER TO zambe;

        -- Index: dynamic_field_refer

        -- DROP INDEX dynamic_field_refer;

        CREATE INDEX dynamic_field_refer
          ON dynamic_field
          USING btree
          (refer COLLATE pg_catalog."default");

        -- Index: dynamic_field_refer_like

        -- DROP INDEX dynamic_field_refer_like;

        CREATE INDEX dynamic_field_refer_like
          ON dynamic_field
          USING btree
          (refer COLLATE pg_catalog."default" varchar_pattern_ops);

        -- Index: dynamic_field_typo

        -- DROP INDEX dynamic_field_typo;

        CREATE INDEX dynamic_field_typo
          ON dynamic_field
          USING btree
          (typo COLLATE pg_catalog."default");

        -- Index: dynamic_field_typo_like

        -- DROP INDEX dynamic_field_typo_like;

        CREATE INDEX dynamic_field_typo_like
          ON dynamic_field
          USING btree
          (typo COLLATE pg_catalog."default" varchar_pattern_ops);
    """)
