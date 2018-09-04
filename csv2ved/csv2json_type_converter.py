import json
from dateutil.parser import parse


def _parse_datetime(data):
    try:
        int(data)
    except ValueError:
        return parse(data).isoformat()
    else:
        raise ValueError


def _parse_date(data):
    try:
        int(data)
    except ValueError:
        return parse(data).strftime("%Y-%m-%d")
    else:
        raise ValueError


def _parse_json(data):
    return json.loads(data)


def _parse_bool(data):
    valid_bool_values = {
        '0': False,
        '1': True,
        'true': True,
        'false': False
    }
    try:
        return valid_bool_values[data.lower()]
    except KeyError:
        raise ValueError


class ConvertCsvDataToJson(object):
    known_types = {
        'string': str,
        'integer': int,
        'float': float,
        'boolean': _parse_bool,
        'date': _parse_date,
        'datetime': _parse_datetime,
        'json': _parse_json
    }

    @classmethod
    def convert(cls, csv_type, data):
        if data == "":
            return None
        if csv_type not in cls.known_types:
            return None
        return cls.known_types[csv_type](data)
