'''
Generate an Abaco-style UUID
'''
import uuid
from hashids import Hashids
HASH_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'


def get_id():
    '''
    Generate an Abaco-style hashid
    '''
    hashids = Hashids(salt=HASH_SALT)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)


# Verified Py3 compatible
