import os

GPG_TEST_HOME_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'gpghome')
REQUIRED_TEST_RECIPIENTS = ['rroy@tucowsinc.com', 'rroy@tucowsinc.com']
TEST_GPG_KEYS = [
    {
        'type': 'pub', 'trust': '-', 'length': '4096', 'algo': '1', 'keyid': 'DD1A348A427C0575',
        'date': '1536084466', 'expires': '', 'dummy': '', 'ownertrust': '-', 'sig': '',
        'uids': ['rajan (rajan for rroy@tucowsinc.com) <rroy@tucowsinc.com>'],
        'sigs': [], 'subkeys': [['DD1A348A427C0575', 'e', 'A6727FF29CAC79E6E23E99ECDD1A348A427C0575']],
        'fingerprint': 'A672 7FF2 9CAC 79E6 E23E  99EC DD1A 348A 427C 0575'
    }
]
