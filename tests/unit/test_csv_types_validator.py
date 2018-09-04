from csv2ved.csv_type_validator import ValidateCsvTypes


class TestValidateCsvTypes(object):

    def test_unknown_type_fails_validation(self):
        assert ValidateCsvTypes.validate('foo', "bar") == "foo is not known type"

    def test_string_validation_always_passes(self):
        test_data = ["123", "True", "1.23", "I'm a string", "", '2020-01-01T12:13:14', '{"foo": "bar"}']

        for data in test_data:
            assert ValidateCsvTypes.validate('string', data) == ""

    def test_int_validation_passes(self):
        test_data = ['', '12345', '-1']

        for data in test_data:
            assert ValidateCsvTypes.validate('integer', data) == ""

    def test_int_validation_fails(self):
        test_data = ['1.2345', '1.0', '1oo']

        for data in test_data:
            assert ValidateCsvTypes.validate('integer', data) == "{} is not a valid integer".format(data)

    def test_float_validation_passes(self):
        test_data = ['', '1.2345', '12345', '1.0', '-1.23']

        for data in test_data:
            assert ValidateCsvTypes.validate('float', data) == ""

    def test_float_validation_fails(self):
        test_data = ['1oo', '1.o', 'True', 'False']

        for data in test_data:
            assert ValidateCsvTypes.validate('float', data) == "{} is not a valid float".format(data)

    def test_bool_validation_passes(self):
        test_data = ['', 'False', '0', 'True', '1']

        for data in test_data:
            assert ValidateCsvTypes.validate('boolean', data) == ""

    def test_bool_validation_fails(self):
        test_data = ["foo"]

        for data in test_data:
            assert ValidateCsvTypes.validate('boolean', data) == "{} is not a valid boolean".format(data)

    def test_date_validation_passes(self):
        test_data = ['', '2018-03-21', '21/3/2018', 'March 3, 2017', '3/21/2017', '2018-03-21T12:13:14']

        for data in test_data:
            assert ValidateCsvTypes.validate('date', data) == ""

    def test_date_validation_fails(self):
        test_data = ['foo', '1234']

        for data in test_data:
            assert ValidateCsvTypes.validate('date', data) == "{} is not a valid date".format(data)

    def test_datetime_validation_passes(self):
        test_data = ['', '2018-03-21', '21/3/2018', 'March 3, 2017', '3/21/2017', '2018-03-21T12:13:14']

        for data in test_data:
            assert ValidateCsvTypes.validate('datetime', data) == ""

    def test_datetime_validation_fails(self):
        test_data = ['foo', '1234']

        for data in test_data:
            assert ValidateCsvTypes.validate('datetime', data) == "{} is not a valid datetime".format(data)

    def test_json_validation_passes(self):
        test_data = ['', '{}', '[]', '{"foo":"bar"}', '{"foo":{"bar":"baz"}}', '{"foo":["bar", "baz"]}']

        for data in test_data:
            assert ValidateCsvTypes.validate('json', data) == ""

    def test_json_validation_fails(self):
        test_data = ['{"foo"}', '{"foo":}', 'not a json at all']

        for data in test_data:
            assert ValidateCsvTypes.validate('json', data) == "{} is not a valid json".format(data)
