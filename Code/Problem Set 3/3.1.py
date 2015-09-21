#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set you work with cities infobox data, audit it, come up with a
cleaning idea and then clean it up. In the first exercise we want you to audit
the datatypes that can be found in some particular fields in the dataset.
The possible types of values can be:
- NoneType if the value is a string "NULL" or an empty string ""
- list, if the value starts with "{"
- int, if the value can be cast to int
- float, if the value can be cast to float, but CANNOT be cast to int.
   For example, '3.23e+07' should be considered a float because it can be cast
   as float but int('3.23e+07') will throw a ValueError
- 'str', for all other values

The audit_file function should return a dictionary containing fieldnames and a 
SET of the types that can be found in the field. e.g.
{"field1: set([float, int, str]),
 "field2: set([str]),
  ....
}

All the data initially is a string, so you have to do some checks on the values
first.
"""
import codecs
import csv
import json
import pprint

CITIES = 'cities.csv'

FIELDS = ["name", "timeZone_label", "utcOffset", "homepage", "governmentType_label", "isPartOf_label", "areaCode", "populationTotal", 
          "elevation", "maximumElevation", "minimumElevation", "populationDensity", "wgs84_pos#lat", "wgs84_pos#long", 
          "areaLand", "areaMetro", "areaUrban"]


def is_none_type(text):
    none_type = False
    if text == "NULL" or text == "":
        none_type = True
    return none_type


def is_list(text):
    return text.startswith('{')


def is_int(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


def is_float(text):
    if not is_int(text):
        try:
            float(text)
            return True
        except ValueError:
            return False
    else:
        return False


def check_fieldtype(field):
    if is_none_type(field):
        return type(None)
    elif is_list(field):
        return type([])
    elif is_int(field):
        return type(1)
    elif is_float(field):
        return type(1.0)
    else:
        return type("")


def audit_file(filename, fields):
    fieldtypes = {}
    with open(filename, 'r') as f:
        rows = csv.DictReader(f)
        # First few rows of the data are not what we need to process.
        for k in range(3):
            rows.next()
        for row in rows:
            for field_name in fields:
                fieldtype = check_fieldtype(row[field_name])
                if field_name in fieldtypes:
                    if fieldtype not in fieldtypes[field_name]:
                        fieldtypes[field_name].add(fieldtype)
                else:
                    fieldtypes[field_name] = set([fieldtype])
    return fieldtypes


def test():
    fieldtypes = audit_file(CITIES, FIELDS)

    pprint.pprint(fieldtypes)

    assert fieldtypes["areaLand"] == set([type(1.1), type([]), type(None)])
    assert fieldtypes['areaMetro'] == set([type(1.1), type(None)])
    
if __name__ == "__main__":
    test()
