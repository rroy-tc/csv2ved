import os
import gnupg
import subprocess

module_directory = os.path.dirname(os.path.realpath(__file__))
GPG_HOME_DIRECTORY = os.path.join(module_directory, 'gpghome')
GPG_PRODUCTION_RECIPIENTS = ['rroy@tucowsinc.com']
GPG_PRODUCTION_KEY_DATA_DIRECTORY = [
    os.path.join(module_directory, 'gpg_keys', 'augmented_data_test.asc'),
    os.path.join(module_directory, 'gpg_keys', 'augmented_service.asc')
]
GPG_NON_PRODUCTION_RECIPIENTS = ['rroy@tucowsinc.com']
GPG_NON_PRODUCTION_KEY_DATA_DIRECTORY = [
    os.path.join(module_directory, 'gpg_keys', 'augmented_data_test.asc')
]


def get_gpg_binary():
    try:
        subprocess.call(["gpg", "--version"], stdout=subprocess.PIPE)
        return "gpg"
    except OSError:
        try:
            subprocess.call(["gpg2", "--version"], stdout=subprocess.PIPE)
            return "gpg2"
        except OSError:
            return False


def public_keys_exist(public_keys, public_key_recipients):
    found = []
    for public_key_recipient in public_key_recipients:
        for key in public_keys:
            for uid in key['uids']:
                if "<{}>".format(public_key_recipient) in uid:
                    found.append(public_key_recipient)

    if found == public_key_recipients:
        return True, ""
    else:
        return False, "missing required public key {}".format(list(set(public_key_recipients).difference(found)))


def import_keys(gpg, key_files):
    try:
        for file in key_files:
            key_data = open(file).read()
            gpg.import_keys(key_data)
    except OSError as e:
        return False, str(e)
    return True, ""


def init_gpg(gnupg_home_dir, key_recipients, public_key_files=None):

    gpg_binary = get_gpg_binary()
    if gpg_binary is False:
        return False, "gpg binary not found, it might not be running on the machine"

    try:
        gpg = gnupg.GPG(gpgbinary=gpg_binary, gnupghome=gnupg_home_dir)
    except OSError as e:
        return False, str(e)
    except ValueError as e:
        return False, str(e)

    if public_key_files:
        result, error = import_keys(gpg, public_key_files)
        if error:
            return result, error

    public_keys = gpg.list_keys(keys=key_recipients)
    result, error = public_keys_exist(public_keys, key_recipients)
    if error:
        return result, error

    return gpg, ""


def generate_output_file_name(source_file_name):
    file_name, extension = os.path.splitext(source_file_name)
    return "{}.ved".format(file_name)


def encrypt(gpg, file_to_encrypt, recipients):
    output_file_name = generate_output_file_name(file_to_encrypt)
    try:
        with open(file_to_encrypt, 'rb') as f:
            status = gpg.encrypt_file(f, recipients=recipients, output=output_file_name, always_trust=True)
        os.remove(file_to_encrypt)
        if status.status == 'encryption ok':
            return output_file_name, status
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
        return None, 'Error encrypting {}\n{}'.format(file_to_encrypt, status.status)
    except OSError as err:
        if os.path.exists(file_to_encrypt):
            os.remove(file_to_encrypt)
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
        return None, 'Error encrypting {}\n{}'.format(file_to_encrypt, err)
