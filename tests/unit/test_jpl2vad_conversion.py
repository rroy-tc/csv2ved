from unittest import mock
import os
import tempfile

from csv2ved import jpl2vad_converter


class TestArchiveJplData(object):

    @classmethod
    def setup_class(cls):
        cls.TMP_DIR = tempfile.mkdtemp()
        cls._vad_filename = os.path.join(cls.TMP_DIR, 'file_YYYYMMDDhhmmss.vad')
        cls._jpl_filename = os.path.join(cls.TMP_DIR, 'file_YYYYMMDDhhmmss.jpl')
        with open(cls._jpl_filename, 'w') as f:
            f.write('')

    @classmethod
    def teardown_class(cls):
        os.remove(cls._jpl_filename)
        os.rmdir(cls.TMP_DIR)

    def test_archiver_with_valid_jpl_file_creates_vad(self):
        result, errors = jpl2vad_converter.archive_jpl_data(self._vad_filename, self._jpl_filename)
        assert result is not None
        assert result == self._vad_filename
        assert os.path.exists(result)
        os.remove(result)

    def test_archiver_with_invalid_jpl_file_exits_and_removes_file(self):
        invalid_jpl_file = '/fake/file.jpl'
        result_filename, errors = jpl2vad_converter.archive_jpl_data(self._vad_filename, invalid_jpl_file)
        assert result_filename is None
        assert errors is not None
        assert "No such file or directory: '{}'".format(invalid_jpl_file) in errors
        assert not os.path.exists(self._vad_filename)

    def test_archiver_causes_error_with_invalid_vad_file(self):
        invalid_vad_file = '/fake/file.vad'
        result_filename, errors = jpl2vad_converter.archive_jpl_data(invalid_vad_file, self._jpl_filename)
        assert result_filename is None
        assert errors is not None
        assert "No such file or directory: '{}'".format(invalid_vad_file) in errors
        assert not os.path.exists(self._vad_filename)

    @mock.patch('zipfile.ZipFile.write')
    def test_zipfile_write_failure(self, mock_zipfile_write):
        mock_zipfile_write.side_effect = OSError("No more disk space available")
        result_filename, errors = jpl2vad_converter.archive_jpl_data(self._vad_filename, self._jpl_filename)
        assert result_filename is None
        assert errors is not None
        assert "No more disk space available" in errors
        assert not os.path.exists(self._vad_filename)

    def test_get_compression_info_fails_with_none_file(self):
        jpl_size, vad_size = jpl2vad_converter.get_compression_info(None)
        assert (jpl_size, vad_size) == (None, None)

    def test_get_compression_info_fails_with_invalid_file(self):
        invalid_vad_file = '/invalid/file.vad'
        jpl_size, vad_size = jpl2vad_converter.get_compression_info(invalid_vad_file)
        assert (jpl_size, vad_size) == (None, None)

    def test_get_compression_info_with_valid_vad_file(self):
        vad_file, errors = jpl2vad_converter.archive_jpl_data(self._vad_filename, self._jpl_filename)
        assert errors is None
        jpl_size, vad_size = jpl2vad_converter.get_compression_info(vad_file)
        os.remove(vad_file)
        assert (jpl_size, vad_size) != (None, None)
        assert type(jpl_size) is int
        assert type(vad_size) is int


class TestConvert(object):

    @classmethod
    def setup_class(cls):
        cls.TMP_DIR = tempfile.mkdtemp()
        cls._vad_filename = os.path.join(cls.TMP_DIR, 'file_YYYYMMDDHHMMSS.vad')
        cls._jpl_filename = os.path.join(cls.TMP_DIR, 'file_YYYYMMDDHHMMSS.jpl')
        with open(cls._jpl_filename, 'w') as f:
            f.write('')

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls._jpl_filename):
            os.remove(cls._jpl_filename)
        os.rmdir(cls.TMP_DIR)

    @mock.patch('csv2ved.jpl2vad_converter.get_compression_info')
    @mock.patch('csv2ved.jpl2vad_converter.archive_jpl_data')
    def test_vad_convert_calls_create_archive_jpl_data_with_proper_args(self, mock_data_archiver,
                                                                        mock_compression_info):
        mock_data_archiver.return_value = self._vad_filename, None
        mock_compression_info.return_value = None, None
        result = jpl2vad_converter.convert(self._jpl_filename)
        assert result is not None
        assert mock_data_archiver.call_args_list == [mock.call(self._vad_filename, self._jpl_filename)]
        assert mock_compression_info.call_args_list == [mock.call(self._vad_filename)]
