import copy
import io
from tests import GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS, TEST_GPG_KEYS
from csv2ved import vad2ved_converter
from unittest import mock


class MockGPG(object):
    def list_keys(self, **kwargs):
        return TEST_GPG_KEYS


class MockEncryptFile(object):

    def __init__(self, status):
        self.status = status


class TestGetGpGBinary(object):

    @mock.patch('subprocess.call')
    def test_function_returns_name_if_gpg_is_running(self, mock_subprocess):
        assert vad2ved_converter.get_gpg_binary() == 'gpg'

    @mock.patch('subprocess.call', side_effect=OSError)
    def test_function_returns_false_if_gpg_is_not_running(self, mock_subprocess):
        assert vad2ved_converter.get_gpg_binary() is False


class TestPublicKeyExists(object):

    def setup(self):
        self.gpg_keys = TEST_GPG_KEYS

    def test_function_returns_true_if_all_keys_exist(self):
        assert vad2ved_converter.public_keys_exist(self.gpg_keys, REQUIRED_TEST_RECIPIENTS) == (True, "")

    def test_function_returns_false_if_any_key_is_missing(self):
        gpg_keys = copy.deepcopy(self.gpg_keys)
        gpg_keys[0]['uids'] = ['test (test for test@tucowsinc.com) <test@tucowsinc.com>']
        expected_result = (False, "missing required public key ['rroy@tucowsinc.com']")
        assert vad2ved_converter.public_keys_exist(gpg_keys, REQUIRED_TEST_RECIPIENTS) == expected_result


class TestImportKeys(object):

    @mock.patch('builtins.open', return_value=io.StringIO('some data'))
    @mock.patch('gnupg.GPG')
    def test_function_calls_library_for_each_file(self, mock_gnupg, mock_open):
        test_keys = ['/gpg_keys/key1', '/gpg_keys/key2']
        assert vad2ved_converter.import_keys(mock_gnupg, test_keys) == (True, "")
        assert mock_gnupg.import_keys.call_count == 2


class TestInitGPG(object):

    @mock.patch('csv2ved.vad2ved_converter.get_gpg_binary', return_value=False)
    def test_returns_false_if_gpg_is_not_running(self, mock_get_gpg_binary):
        expected_result = (False, 'gpg binary not found, it might not be running on the machine')
        assert vad2ved_converter.init_gpg(GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS) == expected_result

    @mock.patch('gnupg.GPG', side_effect=OSError("error message"))
    @mock.patch('csv2ved.vad2ved_converter.get_gpg_binary', return_value=True)
    def test_returns_false_if_binary_is_not_available(self, mock_get_gpg_binary, mock_gnupg):
        assert vad2ved_converter.init_gpg(GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS) == (False, "error message")

    @mock.patch('gnupg.GPG', side_effect=ValueError("error message"))
    @mock.patch('csv2ved.vad2ved_converter.get_gpg_binary', return_value=True)
    def test_returns_false_if_gpg_returns_error(self, mock_get_gpg_binary, mock_gnupg):
        assert vad2ved_converter.init_gpg(GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS) == (False, "error message")

    @mock.patch('gnupg.GPG', return_value=MockGPG())
    @mock.patch('csv2ved.vad2ved_converter.get_gpg_binary', return_value=True)
    @mock.patch('csv2ved.vad2ved_converter.import_keys', return_value=(False, "missing required public key"))
    def test_returns_false_on_import_keys_error(self, mock_import_keys, mock_get_gpg_binary, mock_gnupg):
        expected_result = (False, 'missing required public key')
        keys = ['file1', 'file2']
        assert vad2ved_converter.init_gpg(GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS, keys) == expected_result

    @mock.patch('gnupg.GPG', return_value=MockGPG())
    @mock.patch('csv2ved.vad2ved_converter.get_gpg_binary', return_value=True)
    @mock.patch('csv2ved.vad2ved_converter.public_keys_exist', return_value=(False, "error"))
    def test_returns_false_if_key_does_not_exist(self, mock_keys_exist, mock_get_gpg_binary, mock_gnupg):
        assert vad2ved_converter.init_gpg(GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS) == (False, "error")

    @mock.patch('gnupg.GPG', return_value=MockGPG())
    @mock.patch('csv2ved.vad2ved_converter.get_gpg_binary', return_value=True)
    @mock.patch('csv2ved.vad2ved_converter.public_keys_exist', return_value=(True, ""))
    def test_returns_gpg_object_on_success(self, mock_keys_exist, mock_get_gpg_binary, mock_gnupg):
        expected_result = (mock_gnupg.return_value, "")
        assert vad2ved_converter.init_gpg(GPG_TEST_HOME_DIRECTORY, REQUIRED_TEST_RECIPIENTS) == expected_result


class TestGenerateOutputFileName(object):
    expected_file_name = '/path/to/source_file_YYYYMMDDHHIISS.ved'

    def test_function_generates_expected_name(self):
        source_file_name = '/path/to/source_file_YYYYMMDDHHIISS.vad'
        assert vad2ved_converter.generate_output_file_name(source_file_name) == self.expected_file_name

    def test_function_generates_expected_name_when_no_extension(self):
        source_file_name = '/path/to/source_file_YYYYMMDDHHIISS'
        assert vad2ved_converter.generate_output_file_name(source_file_name) == self.expected_file_name


class TestEncrypt(object):
    def setup_method(self):
        self.filename = 'myfile.vad'

    @mock.patch('os.remove')
    @mock.patch('builtins.open', return_value=io.StringIO())
    @mock.patch('gnupg.GPG')
    def test_function_returns_filename_and_status(self, mock_gnupg, mock_open, mock_remove):
        mock_gnupg.encrypt_file.return_value = MockEncryptFile('encryption ok')
        file, status = vad2ved_converter.encrypt(mock_gnupg, self.filename, REQUIRED_TEST_RECIPIENTS)
        assert 'myfile.ved' == file
        assert 'encryption ok' == status.status

    @mock.patch('os.remove')
    @mock.patch('builtins.open', side_effect=OSError('exception message'))
    @mock.patch('gnupg.GPG')
    def test_function_returns_error_if_source_file_cannot_be_read(self, mock_gnupg, mock_open, mock_remove):
        mock_gnupg.encrypt_file.return_value = MockEncryptFile('encryption ok')
        result = vad2ved_converter.encrypt(mock_gnupg, self.filename, REQUIRED_TEST_RECIPIENTS)
        assert (None, 'Error encrypting myfile.vad\nexception message') == result

    @mock.patch('os.remove')
    @mock.patch('builtins.open', side_effect=OSError('exception message'))
    @mock.patch('gnupg.GPG')
    def test_function_returns_error_if_encryption_fails(self, mock_gnupg, mock_open, mock_remove):
        mock_gnupg.encrypt_file.return_value = MockEncryptFile('key expired')
        result = vad2ved_converter.encrypt(mock_gnupg, self.filename, REQUIRED_TEST_RECIPIENTS)
        assert (None, 'Error encrypting myfile.vad\nexception message') == result
