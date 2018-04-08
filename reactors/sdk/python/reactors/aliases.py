"""
Manage and retrieve alias-to-actor_id mappings

Built on AgaveDB which in turn builds on Agave Metatadata
"""
import re
# from agavedb import AgaveKeyValStore

PREFIX = 'org.sd2e.alias.'


def create_alias_keyname(alias):
    '''Creates the internal key name for an alias'''
    assert alias is not None, "Value for 'alias' cannot be empty"
    return PREFIX + alias.lower()


def remove_alias(db, alias):
    '''Delete an alias from the database'''
    alias_key = create_alias_keyname(alias)
    return db.rem(alias_key)


def set_alias(db, alias, actorid):
    '''Create or update actor => alias mapping'''
    alias_key = create_alias_keyname(alias)
    return db.set(alias_key, actorid)


def get_alias(db, alias):
    '''Get a speciifc alias => actor mapping'''
    alias_key = create_alias_keyname(alias)
    return db.get(alias_key)


def get_aliases(db):
    '''Get all aliases as a alphabetically-sorted list'''
    all_keys = db.getall()
    matched_keys = []
    KEYPREFIX = re.compile('^' + PREFIX, re.UNICODE)
    for k in all_keys:
        if KEYPREFIX.match(k):
            matched_keys.append((re.sub('^' + PREFIX, '', k)).encode())
    matched_keys.sort()
    return matched_keys


def id_from_alias(alias, databaseHandle=None, localOnly=True, timeOut=5):
    '''Given a text alias, return its actor ID

    Searches for keys matching org.sd2e.alias.ALIAS. Returns None on failure
    to resolve alias to ID.
    '''

    assert alias is not None, "'alias' parameter cannot be None"
    assert databaseHandle is not None, "'databaseHandle' cannot be None"

    try:
        _id = get_alias(databaseHandle, alias)
        if _id is not None:
            return _id
    except Exception as e:
        raise Exception(
            "No alias '{}' was found: {}".format(alias, e))
        pass

    return None
