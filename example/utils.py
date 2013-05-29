#!/usr/bin/env python
# encoding: utf-8

def _unpack_fields(obj, ignore_keys=[]):
    all_fields = sorted(obj._meta.fields + obj._meta.many_to_many)
    return [
        field for field in all_fields \
        if not field.name in ignore_keys
    ]
