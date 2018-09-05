import uuid
from csv2ved.csv2ved import validate_company_cmd_line_parameter

COMPANY_ID = str(uuid.uuid4())
INVALID_COMPANY_ID = 'company_id'


def test_validation_passes_when_company_id_is_guid():
    assert validate_company_cmd_line_parameter(COMPANY_ID)


def test_validation_fails_for_invalid_company_id():
    assert not validate_company_cmd_line_parameter(INVALID_COMPANY_ID)
