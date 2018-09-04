import csv
import json
import datetime

import os

from collections import OrderedDict

from csv2ved.csv_type_validator import ValidateCsvTypes
from csv2ved.csv2json_type_converter import ConvertCsvDataToJson

MEMBER_ID_COLUMN = "MEMBER_ID"


def csv_file_iterator(csv_file):
    with csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for line in csv_reader:
            yield [value.strip() for value in line]


def make_json(csv_headers, csv_types, data, loyalty_program_id, member_id_name):
    if len(csv_headers) != len(data):
        return False, "Data length does not match headers"

    augmented_data = {}
    for name, value in zip(csv_headers, data):
        error = ValidateCsvTypes.validate(csv_types[name], value)
        if error:
            return False, error
        try:
            json_value = ConvertCsvDataToJson.convert(csv_types[name], value)
            if name == member_id_name and json_value is None:
                return False, "MEMBER_ID cannot be empty"
            if json_value is not None:
                augmented_data[name] = json_value
        except ValueError:
            return False, "Cannot convert '{}' value '{}' to '{}'".format(name, value, csv_types[name])

    _id = "{}_{}".format(loyalty_program_id, augmented_data[member_id_name])
    augmented_dict = {
        "_id": _id,
        "augmentedData": augmented_data
    }
    return json.dumps(augmented_dict), ""


def generate_output_file_name(data_file_path, now=None):
    now = now or datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    file_name, extension = os.path.splitext(data_file_path)
    return "{}_{}.jpl".format(file_name, now)


def validate_csv_headers(csv_headers):
    for name in csv_headers:
        if name.upper() == MEMBER_ID_COLUMN:
            return True
    return False


def get_csv_types(type_file):
    with type_file:
        csv_reader = csv.reader(type_file, delimiter=',', quotechar='"')
        try:
            names = next(csv_reader)
            types = next(csv_reader)
        except StopIteration:
            return False
    return OrderedDict(zip(names, types))


def validate_csv_types(csv_types, headers):
    expected_types = list(csv_types.keys())
    return expected_types == headers


def validate_member_id_type(csv_types, member_id_column):
    return csv_types[member_id_column] == 'string'


def get_member_id_name(csv_types):
    for name in csv_types.keys():
        if name.upper() == MEMBER_ID_COLUMN:
            return name

    return None


def convert(data_file, type_file, loyalty_program_id, max_number_of_errors=100):

    current_line = 0
    number_of_written_lines = 0
    error_lines = []
    csv_headers = []
    csv_types = get_csv_types(type_file)
    if not csv_types:
        error_lines.append({current_line: "Type file is invalid or empty"})
        return "", number_of_written_lines, error_lines

    member_id_name = get_member_id_name(csv_types)
    output_file_name = generate_output_file_name(data_file.name)

    with open(output_file_name, 'w') as output_file:

        for line in csv_file_iterator(data_file):
            current_line += 1
            if current_line == 1:
                csv_headers = line

                if not validate_csv_headers(csv_headers):
                    error_lines.append({current_line: "Missing required column {}".format(MEMBER_ID_COLUMN)})
                    return "", number_of_written_lines, error_lines

                if not validate_csv_types(csv_types, csv_headers):
                    error_lines.append({current_line: "Headers in data file don't match the types file"})
                    return "", number_of_written_lines, error_lines

                if not validate_member_id_type(csv_types, member_id_name):
                    error_lines.append({current_line: "'{}' type must be string".format(member_id_name)})
                    return "", number_of_written_lines, error_lines

                continue
            if line == []:
                continue
            json_line, error = make_json(csv_headers, csv_types, line, loyalty_program_id, member_id_name)
            if json_line:
                output_file.write("{}\n".format(json_line))
                number_of_written_lines += 1
            else:
                error_lines.append({current_line: error})
                if len(error_lines) >= max_number_of_errors:
                    break

    if error_lines or number_of_written_lines == 0:
        os.remove(output_file_name)
    if current_line == 0:
        error_lines.append({current_line: "{} is empty".format(data_file.name)})
    elif not (error_lines or number_of_written_lines):
        error_lines.append({1: "{} doesn't have data lines".format(data_file.name)})

    return output_file_name, number_of_written_lines, error_lines
