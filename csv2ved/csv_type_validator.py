import json
from dateutil.parser import parse


def _is_integer(data):
    int_value = int(data)
    float_value = float(data)
    if int_value != float_value:
        raise ValueError


def _is_bool(data):
    valid_bool_values = ['0', '1', 'true', 'false']
    if str(data).lower() not in valid_bool_values:
        raise ValueError


def _is_date(data):
    try:
        int(data)
    except ValueError:
        parse(data)
    else:
        raise ValueError


class ValidateCsvTypes(object):
    known_types = {
        'string': str,
        'integer': _is_integer,
        'float': float,
        'boolean': _is_bool,
        'date': _is_date,
        'datetime': _is_date,
        'json': json.loads
    }

    @classmethod
    def validate(cls, csv_type, data):
        if csv_type not in cls.known_types:
            return "{} is not known type".format(csv_type)
        try:
            if data == "":
                return ""
            cls.known_types[csv_type](data)
            return ""
        except ValueError:
            return "{value} is not a valid {csv_type}".format(value=data, csv_type=csv_type)
