"""
Generate Abaco-style human-readable UUIDs

Uses the hashids library and strong random
number generator. These UUIDs are nearly as
unique as UUID4 but are much more readable.
"""

import uuid
from hashids import Hashids

_HASH_SALT = 'eJa5wZlEX4eWU'


def get_id():

    '''Generate a hash id'''
    hashids = Hashids(salt=_HASH_SALT)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)


def is_hashid(identifier):

    '''Tries to validate a UUID'''
    hashids = Hashids(salt=_HASH_SALT)
    dec = hashids.decode(identifier)
    if len(dec) > 0:
        return True
    else:
        return False
