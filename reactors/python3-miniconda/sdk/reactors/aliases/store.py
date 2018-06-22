"""
Manage and retrieve alias-to-actor_id mappings

Built on AgaveDB which in turn builds on Agave Metatadata
"""

from __future__ import print_function
from __future__ import absolute_import
from future.standard_library import install_aliases
install_aliases()

import os
import re
import sys

from past.builtins import basestring

sys.path.insert(0, os.path.dirname(__file__))
from agavedb.keyval import AgaveKeyValStore, AgaveError
from agavedb.uniqueid import get_id

PREFIX = 'tacc-alias-'


class AliasStore(AgaveKeyValStore):

    def _createkey(self, alias):
        '''Creates the internal key name for an alias'''
        # Python2/3 compatible coercion to a "stringy" key name
        if isinstance(alias, bytes):
            alias = str(alias)
        return self.alias_prefix + alias.lower()

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
        """Get a speciifc alias => entity mapping

        Implements a 'me' alias to return self
        """
        if alias.lower() == 'me' or alias.lower() == 'self':
            # Precedence: Abaco actorId then Agave appId
            appid = os.environ.get('AGAVE_APP_ID', None)
            alias_key = os.environ.get('_abaco_actor_id', appid)
            if alias_key is not None and alias_key != '':
                return alias_key
            else:
                raise ValueError("Failed to resolve {}".format(alias))

        try:
            return self.get(self._createkey(alias))
        except ValueError as e:
            raise ValueError("Failed to look up alias {}: {}".format(
                alias, e))

    def get_aliases(self, sort_aliases=True):
        '''Fetch all aliases as a alphabetically-sorted list'''
        all_keys = self.getall(sort_aliases=sort_aliases)
        pattern = to_unicode('^' + self.alias_prefix)
        matched_keys = []
        KEYPREFIX = re.compile(pattern, re.UNICODE)
        for k in all_keys:
            if KEYPREFIX.match(k):
                # ksub =
                # if isinstance(alias, bytes):
                #     alias = str(alias)
                matched_keys.append(re.sub(KEYPREFIX, '', k))
        if sort_aliases is True:
            matched_keys.sort()

        return matched_keys

    def rem_all_aliases(self):
        '''Removes all aliases owned by current user'''
        all_keys = self.deldb()
        return all_keys


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
