import uuid
from csv2ved.csv2ved import validate_lp_cmd_line_parameter

LOYALTY_PROGRAM_ID = str(uuid.uuid4())
INVALID_LOYALTY_PROGRAM_ID = 'lp_id'


def test_validation_passes_when_lp_id_is_guid():
    assert validate_lp_cmd_line_parameter(LOYALTY_PROGRAM_ID)


def test_validation_fails_for_invalid_lp_id():
    assert not validate_lp_cmd_line_parameter(INVALID_LOYALTY_PROGRAM_ID)
