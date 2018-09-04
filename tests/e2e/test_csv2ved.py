import datetime
import os
import uuid
import tempfile
from click import testing as click_testing
from csv2ved import csv2ved
from unittest import mock


temp_log_dir = tempfile.mkdtemp()
current_time = datetime.datetime.today()

DATA_FILE = os.path.join(temp_log_dir, 'data.csv')
TYPE_FILE = os.path.join(temp_log_dir, 'data.csvt')
MISSING_FILE = os.path.join(temp_log_dir, 'foo.bar')
EXPECTED_OUTPUT_JPL_FILE = os.path.join(temp_log_dir, 'data_{}.jpl'.format(current_time.strftime('%Y%m%d%H%M%S')))
EXPECTED_OUTPUT_VAD_FILE = os.path.join(temp_log_dir, 'data_{}.vad'.format(current_time.strftime('%Y%m%d%H%M%S')))
EXPECTED_OUTPUT_VED_FILE = os.path.join(temp_log_dir, 'data_{}.ved'.format(current_time.strftime('%Y%m%d%H%M%S')))
LOYALTY_PROGRAM_ID = str(uuid.uuid4())
INVALID_LOYALTY_PROGRAM_ID = 'lp_id'


def overwrite_test_file_content(filename, content):
    with open(filename, 'w') as data_file:
        data_file.write(content)


class TestCsv2Ved(object):

    def setup_method(self, method):
        overwrite_test_file_content(DATA_FILE, "MEMBER_ID,name,balance\n12345,John Smith,1000\n")
        overwrite_test_file_content(TYPE_FILE, "MEMBER_ID,name,balance\nstring,string,integer\n")

    def teardown_method(self, method):
        os.remove(DATA_FILE)
        os.remove(TYPE_FILE)

    @mock.patch('datetime.datetime')
    def test_script_with_correct_parameters_creates_ved_file(self, datetime_mock):
        datetime_mock.today.return_value = current_time
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 0
        assert '1 lines written' in result.output
        assert '{} archived to {}.'.format(EXPECTED_OUTPUT_JPL_FILE, EXPECTED_OUTPUT_VAD_FILE) in result.output
        assert '{} encrypted to {}'.format(EXPECTED_OUTPUT_VAD_FILE, EXPECTED_OUTPUT_VED_FILE) in result.output

    @mock.patch('datetime.datetime')
    def test_script_creates_non_production_ved_file(self, datetime_mock):
        datetime_mock.today.return_value = current_time
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--prod', False,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 0
        assert '1 lines written' in result.output
        assert '{} archived to {}.'.format(EXPECTED_OUTPUT_JPL_FILE, EXPECTED_OUTPUT_VAD_FILE) in result.output
        assert '{} encrypted to {}'.format(EXPECTED_OUTPUT_VAD_FILE, EXPECTED_OUTPUT_VED_FILE) in result.output

    @mock.patch('datetime.datetime')
    def test_script_does_not_write_corrupted_lines(self, datetime_mock):
        datetime_mock.today.return_value = current_time
        overwrite_test_file_content(DATA_FILE, "MEMBER_ID,name,balance\n12345,John Smith\n")
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'Errors:' in result.output
        assert "line 2: Data length does not match headers" in result.output
        assert 'lines written to output file' not in result.output

    @mock.patch('datetime.datetime')
    def test_script_does_not_parse_file_with_missing_member_id_header(self, datetime_mock):
        datetime_mock.today.return_value = current_time
        overwrite_test_file_content(DATA_FILE, "memberId,name,balance\n12345,John Smith\n")
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'Errors:' in result.output
        assert "line 1: Missing required column MEMBER_ID" in result.output
        assert 'lines written to output file' not in result.output

    def test_script_shows_usage_when_run_without_options(self):
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved, [])
        assert result is not None
        assert result.exit_code == 2
        assert 'Usage: csv2ved [OPTIONS]' in result.output

    def test_script_returns_error_when_lp_parameter_is_missing(self):
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'Error: Missing option "--loyalty-program-id"' in result.output

    def test_script_returns_error_when_lp_parameter_is_not_guid(self):
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', INVALID_LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'Invalid format for loyalty program ID parameter, aborting' in result.output

    def test_script_returns_error_when_file_path_is_incorrect(self):
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', MISSING_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'Could not open file: {file}: No such file or directory'.format(file=MISSING_FILE) in result.output

    @mock.patch('zipfile.ZipFile.write')
    @mock.patch('datetime.datetime')
    def test_scripts_returns_error_when_archiver_fails(self, mock_datetime, mock_zipfile_write):
        mock_zipfile_write.side_effect = OSError
        mock_datetime.today.return_value = current_time
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'Errors occurred during compression:' in result.output

    @mock.patch('csv2ved.vad2ved_converter.init_gpg', return_value=(False, "init_gpg error message"))
    @mock.patch('datetime.datetime')
    def test_scripts_returns_error_when_gpg_is_not_running(self, mock_datetime, mock_init_gpg):
        mock_datetime.today.return_value = current_time
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'init_gpg error message' in result.output

    @mock.patch('csv2ved.vad2ved_converter.encrypt', return_value=(None, "encryption error message"))
    @mock.patch('datetime.datetime')
    def test_scripts_returns_error_when_encryption_fails(self, mock_datetime, mock_encrypt):
        mock_datetime.today.return_value = current_time
        runner = click_testing.CliRunner()
        result = runner.invoke(csv2ved.csv2ved,
                               [
                                   '--data-file', DATA_FILE,
                                   '--type-file', TYPE_FILE,
                                   '--loyalty-program-id', LOYALTY_PROGRAM_ID,
                                   '--no-input'
                               ])
        assert result is not None
        assert result.exit_code == 2
        assert 'encryption error message' in result.output
