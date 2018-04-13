"""
Manage and retrieve alias-to-actor_id mappings

Built on AgaveDB which in turn builds on Agave Metatadata
"""

from __future__ import print_function
from __future__ import absolute_import
from future.standard_library import install_aliases
install_aliases()

import re

from past.builtins import basestring
from agavedb import AgaveKeyValStore

PREFIX = 'tacc-alias-'


class AliasStore(AgaveKeyValStore):

    @classmethod
    def _createkey(cls, alias):
        '''Creates the internal key name for an alias'''
        assert alias is not None, "Value for 'alias' cannot be empty"
        # Python2/3 compatible coercion to a "stringy" key name
        if isinstance(alias, bytes):
            alias = str(alias)
        return PREFIX + alias.lower()

    def rem_alias(self, alias):
        '''Delete an alias from the database'''
        alias_key = self._createkey(alias)
        return self.rem(alias_key)

    def set_alias(self, alias, name):
        '''Create or update actor => alias mapping'''
        alias_key = self._createkey(alias)
        return self.set(alias_key, name)

    def put_alias_acl(self, alias, acl):
        '''Add ACLs to an alias'''
        alias_key = self._createkey(alias)
        return self.setacl(alias_key, acl)

    def get_alias_acls(self, alias, username=None):
        '''List ACLs for an alias, optionally filtering by username'''
        alias_key = self._createkey(alias)
        return self.getacls(alias_key, user=username)

    def rem_alias_acl(self, alias, username=None):
        '''Entirely remove a user's ACL for a given key'''
        alias_key = self._createkey(alias)
        return self.remacl(alias_key, user=username)

    def get_name(self, alias):
        '''Get a speciifc alias => entity name'''
        alias_key = self._createkey(alias)
        return self.get(alias_key)

    def get_aliases(self, sorted=True):
        '''Fetch all aliases as a alphabetically-sorted list'''
        all_keys = self.getall(sorted=sorted)
        pattern = to_unicode('^' + PREFIX)
        matched_keys = []
        KEYPREFIX = re.compile(pattern, re.UNICODE)
        for k in all_keys:
            if KEYPREFIX.match(k):
                # ksub =
                # if isinstance(alias, bytes):
                #     alias = str(alias)
                matched_keys.append(re.sub(KEYPREFIX, '', k))
        if sorted is True:
            matched_keys.sort()
        return matched_keys


def to_unicode(input):
    '''Trivial unicode encoder'''
    input = input.encode().decode('utf-8')
    return input

# def id_from_alias(alias, databaseHandle=None, localOnly=True, timeOut=5):
#     '''Given a text alias, return its actor ID

#     Searches for keys matching org.sd2e.alias.ALIAS. Returns None on failure
#     to resolve alias to ID.
#     '''

#     assert alias is not None, "'alias' parameter cannot be None"
#     assert databaseHandle is not None, "'databaseHandle' cannot be None"

#     try:
#         _id = get_alias(databaseHandle, alias)
#         if _id is not None:
#             return _id
#     except Exception as e:
#         raise Exception(
#             "No alias '{}' was found: {}".format(alias, e))
#         pass

#     return None
