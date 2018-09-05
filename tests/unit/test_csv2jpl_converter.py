import copy
import datetime
import io
import json
import uuid
from collections import OrderedDict
from csv2ved import csv2jpl_converter
from unittest import mock


class TestValidateCsvHeaders(object):
    headers = ["MEMBER_ID", "name", "gender", "age"]

    def test_validation_passes_if_required_column_present(self):
        assert csv2jpl_converter.validate_csv_headers(self.headers) is True

    def test_validation_fails_if_required_column_is_missing(self):
        self.headers[0] = 'memberId'
        assert csv2jpl_converter.validate_csv_headers(self.headers) is False

    def test_member_id_is_case_insensitive(self):
        member_id_names = ['Member_Id', 'member_id', 'MEMBER_ID']
        for name in member_id_names:
            self.headers[0] = name
            assert csv2jpl_converter.validate_csv_headers(self.headers) is True


class TestGetCsvTypes(object):
    valid_type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
    missing_line_type_file = io.StringIO('MEMBER_ID,name,balance')

    def test_valid_type_file_parsed_into_dict(self):
        expected_dict = {
            "MEMBER_ID": "string",
            "name": "string",
            "balance": "integer"
        }
        assert csv2jpl_converter.get_csv_types(self.valid_type_file) == expected_dict

    def test_get_csv_types_returns_false_for_invalid_type_file(self):
        assert csv2jpl_converter.get_csv_types(self.missing_line_type_file) is False


class TestValidateCsvTypes(object):
    csv_types = OrderedDict([("name", "string"), ("MEMBER_ID", "string"), ("balance", "integer"), ("userData", "json")])

    def test_validation_passes_if_types_and_data_match(self):
        headers = ["name", "MEMBER_ID", "balance", "userData"]
        assert csv2jpl_converter.validate_csv_types(self.csv_types, headers) is True

    def test_validation_fails_if_the_order_does_not_match(self):
        headers = ["MEMBER_ID", "name", "balance", "userData"]
        assert csv2jpl_converter.validate_csv_types(self.csv_types, headers) is False

    def test_validation_fails_if_headers_missing_a_column(self):
        headers = ["name", "MEMBER_ID", "balance"]
        assert csv2jpl_converter.validate_csv_types(self.csv_types, headers) is False

    def test_validation_fails_if_headers_have_extra_column(self):
        headers = ["name", "MEMBER_ID", "balance", "userData", "foo"]
        assert csv2jpl_converter.validate_csv_types(self.csv_types, headers) is False


class TestGetMemberIdName(object):
    csv_types = {"name": "string", "balance": "string"}

    def test_returns_member_id_column_name(self):
        member_id_names = ['Member_Id', 'member_id', 'MEMBER_ID']
        for name in member_id_names:
            self.csv_types[name] = "string"
            assert csv2jpl_converter.get_member_id_name(self.csv_types) == name
            del(self.csv_types[name])

    def test_returns_none_if_member_id_is_missing(self):
        assert csv2jpl_converter.get_member_id_name(self.csv_types) is None


class TestValidateMemberIdType(object):
    member_id_column = 'MEMBER_ID'
    valid_csv_types = {
        member_id_column: "string",
        "balance": "int"
    }

    invalid_csv_types = {
        member_id_column: "int",
        "balance": "int"
    }

    def test_validate_member_id_type_returns_true(self):
        assert csv2jpl_converter.validate_member_id_type(self.valid_csv_types, self.member_id_column) is True

    def test_validate_member_id_type_returns_false(self):
        assert csv2jpl_converter.validate_member_id_type(self.invalid_csv_types, self.member_id_column) is False


class TestMakeJson(object):
    headers = [
        "MEMBER_ID",
        "name",
        "balance",
        "risk_factor",
        "opt_in",
        "dob",
        "transaction_time",
        "userData"
    ]
    csv_types = {
        "MEMBER_ID": "string",
        "name": "string",
        "balance": "integer",
        "risk_factor": "float",
        "opt_in": "boolean",
        "dob": "date",
        "transaction_time": "datetime",
        "userData": "json"
    }
    member_id_column = "MEMBER_ID"
    data = [
        "12345",
        "John",
        "100",
        "0.25",
        "True",
        "1972-05-15T15:08:56",
        "2017-10-21T12:13:14",
        '{"foo":"bar"}'
    ]
    company_id = str(uuid.uuid4())

    def test_function_returns_json_if_validation_passes(self):
        expected_result = {
            "_id": "{}_12345".format(self.company_id),
            "augmentedData": {
                "name": "John",
                "MEMBER_ID": "12345",
                "balance": 100,
                "risk_factor": 0.25,
                "opt_in": True,
                "dob": "1972-05-15",
                "transaction_time": "2017-10-21T12:13:14",
                "userData": {
                    "foo": "bar"
                }
            }
        }
        json_result, error = csv2jpl_converter.make_json(
            self.headers, self.csv_types, self.data, self.company_id, self.member_id_column)
        assert json.loads(json_result) == expected_result
        assert error == ""

    def test_function_skips_empty_data(self):
        data = copy.deepcopy(self.data)
        data[6] = ""
        expected_result = {
            "_id": "{}_12345".format(self.company_id),
            "augmentedData": {
                "name": "John",
                "MEMBER_ID": "12345",
                "balance": 100,
                "risk_factor": 0.25,
                "opt_in": True,
                "dob": "1972-05-15",
                "userData": {
                    "foo": "bar"
                }
            }
        }
        json_result, error = csv2jpl_converter.make_json(
            self.headers, self.csv_types, data, self.company_id, self.member_id_column)
        assert json.loads(json_result) == expected_result
        assert error == ""

    def test_function_returns_error_if_member_id_is_empty(self):
        data = copy.deepcopy(self.data)
        data[0] = ""
        expected_result = (False, "MEMBER_ID cannot be empty")
        assert csv2jpl_converter.make_json(
            self.headers, self.csv_types, data, self.company_id, self.member_id_column) == expected_result

    def test_function_returns_error_if_headers_and_data_have_different_length(self):
        corrupted_data = copy.deepcopy(self.data)
        corrupted_data.append("foo")
        expected_result = (False, "Data length does not match headers")
        assert csv2jpl_converter.make_json(
            self.headers, self.csv_types, corrupted_data, self.company_id, self.member_id_column) == expected_result

    def test_function_returns_error_if_data_validation_fails(self):
        corrupted_data = corrupted_data = copy.deepcopy(self.data)
        corrupted_data[7] = "one thousand points"
        expected_result = (False, "one thousand points is not a valid json")
        assert csv2jpl_converter.make_json(
            self.headers, self.csv_types, corrupted_data, self.company_id, self.member_id_column) == expected_result

    @mock.patch('csv2ved.csv2json_type_converter.ConvertCsvDataToJson.convert', side_effect=ValueError)
    def test_function_returns_error_if_data_conversion_fails(self, mock_csv2json_convert):
        expected_result = (False, "Cannot convert 'MEMBER_ID' value '12345' to 'string'")
        assert csv2jpl_converter.make_json(
            self.headers, self.csv_types, self.data, self.company_id, self.member_id_column) == expected_result


class TestGenerateOutputFileName(object):
    data_file_name = "/path/to/myfile.csv"
    now = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    expected_name = "/path/to/myfile_{}.jpl".format(now)

    def test_function_generates_expected_name(self):
        generated_name = csv2jpl_converter.generate_output_file_name(self.data_file_name, self.now)
        assert generated_name == self.expected_name

    def test_function_generates_expected_name_when_no_extension(self):
        data_file_name_no_extension = "/path/to/myfile"
        generated_name = csv2jpl_converter.generate_output_file_name(data_file_name_no_extension, self.now)
        assert generated_name == self.expected_name


class TestCsvFileIterator(object):

    def test_csv_iterator_reads_all_lines(self):
        data_file = io.StringIO('MEMBER_ID,name,balance\n12345,John,100')

        csv_lines = []
        for line in csv2jpl_converter.csv_file_iterator(data_file):
            csv_lines.append(line)

        assert len(csv_lines) == 2
        assert csv_lines[0] == ["MEMBER_ID", "name", "balance"]
        assert csv_lines[1] == ["12345", "John", "100"]

    def test_csv_iterator_parses_qoutes(self):
        data_file = io.StringIO('"MEMBER_ID",name,"balance"\n12345,"John Smith",100')

        csv_lines = []
        for line in csv2jpl_converter.csv_file_iterator(data_file):
            csv_lines.append(line)

        assert csv_lines[0] == ["MEMBER_ID", "name", "balance"]
        assert csv_lines[1] == ["12345", "John Smith", "100"]

    def test_csv_iterator_strips_out_leading_and_trailing_spaces_and_tabs(self):
        data_file = io.StringIO('MEMBER_ID,\tname,\tbalance\n12345,"\tJohn\tSmith ", 100 ')

        csv_lines = []
        for line in csv2jpl_converter.csv_file_iterator(data_file):
            csv_lines.append(line)

        assert csv_lines[0] == ["MEMBER_ID", "name", "balance"]
        assert csv_lines[1] == ["12345", "John\tSmith", "100"]


class TestConverter(object):

    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_converts_valid_csv_file(self, mock_generate_output_file_name, mock_open):
        data_file = io.StringIO('MEMBER_ID,name,balance\n12345,John,100')
        data_file.name = ""
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("/path/to/myfile_XYZ.jpl", 1, []) == result

    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_skips_empty_lines_without_errors(self, mock_generate_output_file_name, mock_open):
        data_file = io.StringIO('MEMBER_ID,name,balance\n\n12345,John,100\n\n')
        data_file.name = ""
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("/path/to/myfile_XYZ.jpl", 1, []) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_rejects_corrupted_csv_lines(self, mock_generate_output_file_name, mock_open, mock_remove):
        data_file = io.StringIO('MEMBER_ID,name,balance\n12345,John\n12345,Jane,1000')
        data_file.name = ""
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("/path/to/myfile_XYZ.jpl", 1, [{2: 'Data length does not match headers'}]) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_rejects_csv_file_with_no_data(self, mock_generate_output_file_name, mock_open, mock_remove):
        data_file = io.StringIO('MEMBER_ID,name,balance')
        data_file.name = "/path/to/myfile.csv"
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("/path/to/myfile_XYZ.jpl", 0, [{1: "/path/to/myfile.csv doesn't have data lines"}]) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_rejects_file_with_just_empty_data_rows(self, mock_generate_file_name, mock_open, mock_remove):
        data_file = io.StringIO('MEMBER_ID,name,balance\n\n\n\n\n')
        data_file.name = "/path/to/myfile.csv"
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("/path/to/myfile_XYZ.jpl", 0, [{1: "/path/to/myfile.csv doesn't have data lines"}]) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_rejects_empty_csv_file(self, mock_generate_output_file_name, mock_open, mock_remove):
        data_file = io.StringIO('')
        data_file.name = "/path/to/myfile.csv"
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("/path/to/myfile_XYZ.jpl", 0, [{0: "/path/to/myfile.csv is empty"}]) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    def test_converter_stops_if_type_file_is_empty(self, mock_open, mock_remove):
        data_file = io.StringIO('MEMBER_ID,name,balance\n12345,John\n12345,Jane,1000')
        type_file = io.StringIO('')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id)
        assert ("", 0, [{0: 'Type file is invalid or empty'}]) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_stops_after_max_errors(self, mock_generate_output_file_name, mock_open, mock_remove):
        data_file = io.StringIO('MEMBER_ID,name,balance\n64583,Sally\n33445,Peter,1000,200\n10101,Phil')
        data_file.name = ""
        type_file = io.StringIO('MEMBER_ID,name,balance\nstring,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id, 2)
        expected_errors = [{2: 'Data length does not match headers'}, {3: 'Data length does not match headers'}]
        assert ("/path/to/myfile_XYZ.jpl", 0, expected_errors) == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('csv2ved.csv2jpl_converter.generate_output_file_name', return_value="/path/to/myfile_XYZ.jpl")
    def test_converter_returns_error_if_member_id_type_is_not_string(
            self, generate_output_file_name, mock_open, mock_remove):
        data_file = io.StringIO('MEMBER_ID,name,balance\n64583,Sally\n33445,Peter,1000,200\n10101,Phil')
        data_file.name = ""
        type_file = io.StringIO('MEMBER_ID,name,balance\nint,string,integer')
        company_id = str(uuid.uuid4())
        result = csv2jpl_converter.convert(data_file, type_file, company_id, 2)
        assert ("", 0, [{1: "'MEMBER_ID' type must be string"}]) == result
