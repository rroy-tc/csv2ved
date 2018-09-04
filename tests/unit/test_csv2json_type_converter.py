import copy
import pytest
from csv2ved.csv2json_type_converter import ConvertCsvDataToJson


class TestConvertCsvDataToJson(object):

    @staticmethod
    def _convert(csv_type, data):
        return [ConvertCsvDataToJson.convert(csv_type, value) for value in data]

    def test_converter_returns_none_for_unknown_type(self):
        assert ConvertCsvDataToJson.convert("foo", "bar") is None

    def test_converter_returns_none_for_empty_data(self):
        assert ConvertCsvDataToJson.convert("string", "") is None

    def test_convert_to_string_returns_string(self):
        test_data = ["123", "True", "1.23", "I'm a string", '2020-01-01T12:13:14', '{"foo": "bar"}']
        expected_data = copy.deepcopy(test_data)
        assert expected_data == self._convert('string', test_data)

    def test_convert_to_int_returns_integer(self):
        test_data = ["123", "-20"]
        expected_data = [123, -20]
        assert expected_data == self._convert('integer', test_data)

    def test_convert_to_int_raises_exception_for_non_integer_values(self):
        test_data = ["True", "1.23", "I'm a string", '2020-01-01T12:13:14']
        for data in test_data:
            with pytest.raises(ValueError):
                ConvertCsvDataToJson.convert("integer", data)

    def test_convert_to_float_passes(self):
        test_data = ["123", "123.0", "123.5", "-20", "-20.0", "-20.5"]
        expected_data = [123.0, 123.0, 123.5, -20.0, -20.0, -20.5]
        assert expected_data == self._convert('float', test_data)

    def test_convert_to_float_raises_exception_for_non_numeric_values(self):
        test_data = ["True", "I'm a string", '2020-01-01T12:13:14']
        for data in test_data:
            with pytest.raises(ValueError):
                ConvertCsvDataToJson.convert("float", data)

    def test_convert_to_bool_returns_boolean_value(self):
        test_data = ["1", "0", "True", "False", "true", "false"]
        expected_data = [True, False, True, False, True, False]
        assert expected_data == self._convert('boolean', test_data)

    def test_convert_to_bool_raises_exception(self):
        test_data = ["foo", "1.0", ""]
        with pytest.raises(ValueError):
            for data in test_data:
                ConvertCsvDataToJson.convert("boolean", data)

    def test_convert_to_date_returns_to_yyyy_mm_dd_strings(self):
        test_data = ['2020-03-01T12:13:14', '2020-03-01', 'Mar 1, 2020', '3/1/2020']
        expected_data = ['2020-03-01', '2020-03-01', '2020-03-01', '2020-03-01']
        assert expected_data == self._convert('date', test_data)

    def test_convert_to_date_raises_if_string_is_not_a_date(self):
        test_data = ['4', "I'm a string", 'Fab 3, 2020']
        for data in test_data:
            with pytest.raises(ValueError):
                ConvertCsvDataToJson.convert("date", data)

    def test_convert_to_datetime_returns_iso_date_strings(self):
        test_data = ['2020-03-01T12:13:14', '2020-03-01', 'Mar 1, 2020, 12:13:14', '3/1/2020 12:13:14']
        expected_data = ['2020-03-01T12:13:14', '2020-03-01T00:00:00', '2020-03-01T12:13:14', '2020-03-01T12:13:14']
        assert expected_data == self._convert('datetime', test_data)

    def test_convert_to_datetime_raises_if_string_is_not_a_datetime(self):
        test_data = ['4', "I'm a string", 'Fab 3, 2020']
        for data in test_data:
            with pytest.raises(ValueError):
                ConvertCsvDataToJson.convert("datetime", data)

    def test_convert_to_json_returns_json_string(self):
        test_data = ['{}', '[]', '{"foo":"bar"}', '{"foo":{"bar":"baz"}}', '{"foo":["bar","baz"]}']
        expected_data = [{}, [], {"foo": "bar"}, {"foo": {"bar": "baz"}}, {"foo": ["bar", "baz"]}]
        assert expected_data == self._convert('json', test_data)

    def test_convert_to_json_raises_if_string_is_not_a_json(self):
        test_data = ['{"foo"}', '{"foo":}', "I'm a string", '2020-03-01T12:13:14']
        for data in test_data:
            with pytest.raises(ValueError):
                ConvertCsvDataToJson.convert("json", data)
