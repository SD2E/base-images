"""
Generates Abaco-style UUIDs using the
Hashids library. These give unique
IDs without the line noise of UUID4.
"""

import uuid
from hashids import Hashids

HASH_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'


def get_id():
    """
    Generate a random uuid.
    """
    hashids = Hashids(salt=HASH_SALT)
    _uuid = uuid.uuid1().int >> 64
    return hashids.encode(_uuid)
