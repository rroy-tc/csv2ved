import os
import zipfile

JPL_FILENAME_IN_ARCHIVE = 'data.jpl'


def get_compression_info(vad_filename):
    try:
        archive = zipfile.ZipFile(vad_filename)
        archive_info = archive.getinfo(JPL_FILENAME_IN_ARCHIVE)
        return archive_info.file_size, archive_info.compress_size
    except (OSError, AttributeError):
        return None, None


def archive_jpl_data(vad_filename, jpl_filename_for_archive):
    try:
        with zipfile.ZipFile(vad_filename, mode='w', compression=zipfile.ZIP_DEFLATED) as vad_archive:
                vad_archive.write(jpl_filename_for_archive, arcname=JPL_FILENAME_IN_ARCHIVE)
                return vad_archive.filename, None
    except OSError as err:
        if os.path.exists(vad_filename):
            os.remove(vad_filename)
        return None, 'Error compressing {}\n{}'.format(jpl_filename_for_archive, err)


def convert(jpl_data_filename):
    filename_without_extension = os.path.splitext(jpl_data_filename)[0]
    vad_filename = "{}.vad".format(filename_without_extension)
    archive_filename, errors = archive_jpl_data(vad_filename, jpl_data_filename)
    original_jpl_size, vad_compress_size = get_compression_info(archive_filename)
    if os.path.exists(jpl_data_filename):
        os.remove(jpl_data_filename)
    return archive_filename, errors, original_jpl_size, vad_compress_size
