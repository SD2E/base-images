"""
AgaveDB is multiuser-aware key/value store built using the Agave metadata web service API.

The library interface is modeled on pickledb, which is inspired by Redis. Eventually, it will support Agave-based permissions and sharing. If you need a more
document-oriented solution, you can utilize the underlying Agave `metadata` service.

Usage:
```python
from agavedb import AgaveKeyValStore
```
"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import object
from past.builtins import basestring
import re
import json
import logging
import time
import sys
import os

from agavepy.agave import AgaveError

sys.path.insert(0, os.path.dirname(__file__))
import uniqueid

__version__ = '0.15a'

PREFIX = 'kvs_v3'
LOGLEVEL = 'ERROR'
SEP = '/'
TTL = 86400
VALID_PEMS = ['read', 'write', 'execute']
VALID_ROLE_USERNAMES = ['world', 'public']

_MAX_VAL_BYTES = 32768
_MIN_KEY_BYTES = 4
_MAX_KEY_BYTES = 2048
_RE_KEY_NAMES = re.compile('^[\S]+$', re.UNICODE)


class AgaveKeyValStore(object):

    """An AgaveKeyValStore instance. Requires an active Agave client"""

    def __init__(self, agaveClient, keyPrefix=PREFIX,
                 aliasPrefix='', logLevel=LOGLEVEL):
        '''Initialize class with a valid Agave API client'''
        self.client = agaveClient
        self.default_ttl = TTL
        self.prefix = keyPrefix
        self.alias_prefix = aliasPrefix
        self.separator = SEP
        FORMAT = "[%(levelname)s] %(asctime)s: %(message)s"
        DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
        self.logging = logging.getLogger('AgaveKeyValStore')
        stderrLogger = logging.StreamHandler()
        stderrLogger.setLevel(logLevel)
        stderrLogger.setFormatter(
            logging.Formatter(FORMAT, datefmt=DATEFORMAT))
        self.logging.addHandler(stderrLogger)

    def set(self, key, value):
        '''Set the string or numeric value of a key'''
        try:
            return self._set(key, value)
        except Exception as e:
            self.logging.debug("set failed {}={}: {}".format(key, value, e))
            raise ValueError("Failed to set value of {}: {}".format(key, e))

    def get(self, key):
        '''Get the value of a key'''
        try:
            return self._get(key)['value']
        except Exception as e:
            self.logging.debug("get failed {}".format(e))
            raise ValueError("Failed to get value of {}: {}".format(key, e))

    def getall(self, sort_aliases=True):
        '''Return a list of all keys user owns or has access to'''
        namespaces = False
        try:
            return self._getall(namespaces)
        except Exception as e:
            self.logging.debug("failed to getall".format(e))
            raise ValueError("Error in getall: {}".format(e))

    def rem(self, key):
        '''Delete a key (assuming it is owned by the user)'''
        try:
            return self._rem(key)
        except Exception as e:
            self.logging.debug("failed to rem {}: {}".format(key, e))
            raise KeyError("Error in rem {}: {}".format(key, e))

    def deldb(self):
        '''Delete all user-owned keys'''
        try:
            return self._remall()
        except Exception as e:
            self.logging.debug("failed to deldb: {}".format(e))
            raise ValueError("Error in deldb: {}".format(e))

    def setacl(self, key, acl):
        """
        Set an ACL on a given key

        Positional parameters:
        key - str - Key to manage permissions on
        acl - dict - Valid permissions object

        {'read': bool, 'write': bool}

        Returns:
        Boolean True on success, and Exception + False on failure
        """
        try:
            self.validate_acl(acl)
            return self._setacl(key, acl)
        except Exception as e:
            self.logging.debug(
                "Failed to set ACl({}, {}): {}".format(key, acl, e))
            return False

    def remacl(self, key, user):
        """
        Remove an ACL on a key for a given user

        Positional parameters:
        key - str - Key to manage permissions on
        user - str - Username whose ACL should be dropped

        Returns:
        Boolean True on success, and Exception + False on failure
        """
        acl = {'username': user,
               'permission': {'read': None, 'write': None, 'execute': None}}
        try:
            return self._setacl(key, acl)
        except Exception as e:
            self.logging.debug(
                "Failed to remove ACL({}, {}): {}".format(key, user, e))
            return False

    def getacls(self, key, user=None):
        """
        Get the ACLs for a given key

        Keywork parameters:
        user - str - Return ACL only for this username
        """
        try:
            return self._getacls(key, user)
        except Exception as e:
            self.logging.debug("Failed to getacls: {}".format(e))
            return []

    def _namespace(self, keyname):
        """Namespaces a key

        e.g.) keyname => _agavedb/keyname#username
        """
        if self._key_is_valid(keyname):
            _keyname = keyname
            _keyname = self.prefix + self.separator + _keyname + \
                '#' + self._username()
            return _keyname
        else:
            self.logging.debug("failed to namespace {}".format(keyname))
            raise ValueError("Can't namespace {}: {}".format(keyname))

    def _rev_namespace(self, keyname, removeusername=True):
        """Reverse namespacing of a key's internal representation.

        e.g.) _agavedb/keyname#username => keyname
        """
        assert isinstance(keyname, basestring), \
            "key type must be string or unicode (type: {})".format(
                self._type(keyname))

        prefix = '^' + self.prefix + self.separator
        suffix = '#' + self._username() + '$'

        try:
            keyname = re.sub(prefix, '', keyname)
            if removeusername:
                keyname = re.sub(suffix, '', keyname)
            return keyname
        except Exception as e:
            self.logging.debug("failed to reverse namespace {}: {}".format(
                keyname, e))
            raise ValueError("Can't reverse namespace {}: {}".format(
                keyname, e))

    def _slugify(self, value, allow_unicode=False):
        """
        Convert a string to a conservatively URL-safe version

        Converts to ASCII if 'allow_unicode' is False. Converts
        whitespace to hyphens. Removes characters that aren't
        alphanumerics, underscores, or hyphens. Converts to
        lowercase. Strips leading and trailing whitespace.
        """
        import unicodedata
        try:
            value = str(value)
            if allow_unicode:
                value = unicodedata.normalize('NFKC', value)
            else:
                value = unicodedata.normalize(
                    'NFKD', value).encode('ascii', 'ignore').decode('ascii')
            value = re.sub(r'[^\w\s-]', '', value).strip().lower()
            value = re.sub(r'[-\s]+', '-', value)
            return value
        except Exception as e:
            self.logging.debug("failed to slugify {}: {}".format(value, e))
            raise ValueError("Failed to slugify {}: {}".format(value, e))

    def _type(self, obj):
        '''Return the type name of a Python object'''
        try:
            return type(obj).__name__
        except Exception as e:
            self.logging.debug("failed to get type for {}: {}".format(obj, e))
            raise TypeError("Failed to get type for {}: {}".format(obj, e))

    def _username(self):
        '''Return the current Agave API username'''
        try:
            return self.__get_api_username()
        except Exception as e:
            raise AgaveError("Failed to discover username: {}".format(e))

    def _get(self, key):
        '''Get value by key name.'''
        shares = False
        key_name = self._namespace(key)
        username = self._username()
        # An Agave metadata object, not yet the value
        if shares:
            _regex = "^{}/{}#".format(self.prefix, key)
            query = json.dumps({'name': {'$regex': _regex, '$options': 'i'}})
        else:
            query = json.dumps({'name': key_name})

        try:
            key_objs = self.client.meta.listMetadata(q=query)
            assert isinstance(key_objs, list)
        except Exception as e:
            self.logging.debug("Failed to listMetadata")
            raise AgaveError("Failed at meta.listMetadata: {}".format(e))

        key_objs_owner = []
        key_objs_other = []
        for key_obj in key_objs:
            if key_obj['owner'] == username:
                key_objs_owner.append(key_obj)
            else:
                key_objs_other.append(key_obj)
        key_objs_merged = key_objs_owner + key_objs_other
        if len(key_objs_merged) > 0:
            return key_objs_merged[0]
        else:
            raise KeyError("No such key: {}".format(key))

    def _set(self, key, value):
        '''Update/write value to a key'''
        key_name = self._namespace(key)
        key_uuid = None

        if not self._value_is_valid(value):
            raise ValueError(
                "Invalid type for {} (type: {})".format(
                    key, self._type(value)))

        key_uuid_obj = {}
        try:
            key_uuid_obj = self._get(key)
            key_uuid = key_uuid_obj['uuid']
        except KeyError:
            self.logging.debug("Key {} didn't exist".format(key))
            pass

        current_time = int(time.time())
        if '_created' in key_uuid_obj:
            created_t = key_uuid_obj['_created']
            expires_t = current_time + self.default_ttl
        else:
            created_t = current_time
            expires_t = created_t + self.default_ttl

        try:
            value = str(value)
        except Exception as e:
            raise TypeError("Couldn't coerce {} to unicode: {}".format(
                value, e))

        try:
            value = self._stringify(value)
        except Exception as e:
            raise ValueError("Couldn't stringify {}: {}".format(value, e))

        # our metadata record with timestamps
        meta = json.dumps({'name': key_name,
                           'value': value,
                           '_created': created_t,
                           '_expires': expires_t,
                           '_ttl': self.default_ttl})

        if key_uuid is None:
            # Create
            try:
                self.client.meta.addMetadata(body=meta)
            except Exception as e:
                self.logging.debug("Error writing key {}: {}".format(key, e))
                raise AgaveError("Failed at meta.addMetadata: {}".format(e))
        else:
            # Update
            try:
                self.client.meta.updateMetadata(uuid=key_uuid, body=meta)
            except Exception as e:
                self.logging.debug("Error updating key {}: {}".format(key, e))
                raise AgaveError("Failed at meta.updateMetadata: {}".format(e))

        return key

    def _getall(self, namespace=False, sort_aliases=True, uuids=False):
        '''Fetch and return all keys visible to the user'''
        all_keys = []
        _regex = "^{}/*".format(self.prefix)
        query = json.dumps({'name': {'$regex': _regex, '$options': 'i'}})
        # collection of Agave metadata objects
        try:
            key_objs = self.client.meta.listMetadata(q=query)
            assert isinstance(key_objs, list)
        except Exception as e:
            self.logging.debug("Failed to listMetadata")
            raise AgaveError("Failed at meta.listMetadata: {}".format(e))

        for key_obj in key_objs:
            if uuids:
                all_keys.append(key_obj['uuid'])
            elif namespace:
                all_keys.append(key_obj['name'])
            else:
                all_keys.append(self._rev_namespace(key_obj['name']))

        if sort_aliases:
            all_keys.sort()

        return all_keys

    def _rem(self, key):
        '''Delete a key from a user's namespace'''
        key_uuid = None
        try:
            key_uuid = self._get(key)
            key_uuid = key_uuid['uuid']
        except KeyError:
            raise KeyError("No such key: {}".format(key))
        except Exception as e:
            raise ValueError("Failed to validate key {}: {}".format(key, e))

        try:
            self._rem_by_uuid(key_uuid)
            return True
        except Exception as e:
            raise KeyError("Failed to delete {}: {}".format(key, e))

    def _rem_by_uuid(self, key_uuid):
        '''Delete key by its UUID'''
        try:
            self.client.meta.deleteMetadata(uuid=key_uuid)
            return True
        except Exception as e:
            raise AgaveError("Failed to delete UUID {}: {}}".format(
                key_uuid, e))

    def _remall(self):
        '''Remove all the user's keys'''
        try:
            key_list = self._getall(uuids=True)
            for key_uuid in key_list:
                self._rem_by_uuid(key_uuid)
            return []
        except Exception:
            raise ValueError("Failed to remove all {}/* keys".format(
                self.prefix))

    def _setacl(self, key, acl):
        '''Add or update an ACL to a key'''
        key_uuid = None
        key_uuid_obj = {}
        try:
            key_uuid_obj = self._get(key)
            key_uuid = key_uuid_obj['uuid']
        except KeyError:
            self.logging.debug("Key {} not found".format(key))
            raise KeyError("Key {} not found".format(key))

        pem = self.to_text_pem(acl)
        meta = json.dumps(pem, indent=0)
        try:
            self.client.meta.updateMetadataPermissions(
                uuid=key_uuid, body=meta)
            return True
        except Exception as e:
            self.logging.debug(
                "Error setting ACL for {}: {}".format(key, e))
            raise AgaveError("Failed to set ACL on {}: {}".format(key, e))

    def _getacls(self, key, user=None):
        '''List ACLs on a given key'''
        key_uuid = None
        key_uuid_obj = {}
        acls = []

        try:
            key_uuid_obj = self._get(key)
            key_uuid = key_uuid_obj['uuid']
        except KeyError:
            self.logging.debug("Key {} not found".format(key))
            raise KeyError("Key {} not found".format(key))
        try:
            resp = self.client.meta.listMetadataPermissions(uuid=key_uuid)
            for acl in resp:
                formatted_acl = {'username': acl.get('username'),
                                 'permission': acl.get('permission')}
                if user is None:
                    acls.append(formatted_acl)
                else:
                    if user == acl.get('username'):
                        acls.append(formatted_acl)
                    # show the user is inheriting world acl
                    elif 'world' == acl.get('username'):
                        acls.append(formatted_acl)
            return acls
        except Exception as e:
            self.logging.debug(
                "Failed getting ACLs for for {}: {}".format(key, e))
            raise AgaveError("Failed to get ACL for {}: {}".format(key, e))

    def _value_is_valid(self, value):
        '''Value must be a string. Others may be supported later.'''
        assert isinstance(value, basestring), \
            "value must be string or unicode (type: {})".format(
                self._type(value))
        assert len(value) <= _MAX_VAL_BYTES, \
            "value must be <= {} (length: {})".format(len(value))
        return True

    def _key_is_valid(self, key):
        '''Enforce key naming restrictions'''

        # type
        assert isinstance(key, basestring), \
            "key type must be string or unicode (type: {})".format(
                self._type(key))

        # character set
        assert _RE_KEY_NAMES.match(key), \
            "key may only contain non-whitespace characters"
        assert self.separator not in key, "key may not contain '{}'".format(
            self.separator)
        assert '#' not in key, "key may not contain #"

        # length
        assert len(key) <= _MAX_KEY_BYTES, \
            "key must be <= {} characters (length: {})".format(
                _MAX_KEY_BYTES, len(key))
        assert len(key) >= _MIN_KEY_BYTES, \
            "key must be >= {} characters (length: {})".format(
                _MIN_KEY_BYTES, len(key))

        return True

    def _stringify(self, value):
        '''Coerce a value to a string type before sending to MongoDB'''
        return '"' + value + '"'

    @classmethod
    def create_key_name(cls):
        '''Create a unique, human-friendly key name'''
        return uniqueid.get_id()


    @classmethod
    def to_text_pem(cls, acl):
        pem = {"username": acl.get('username')}
        permission = acl.get('permission')
        perm_str = u'NONE'
        r, w, x = permission.get('read', False), \
            permission.get('write', False), \
            permission.get('execute', False)

        if r:
            perm_str = u'READ'
        if w:
            perm_str = u'READ_WRITE'
        if x:
            perm_str = u'READ_EXECUTE'
        if r and w:
            perm_str = u'READ_WRITE'
        if r and x:
            perm_str = u'READ_EXECUTE'
        if r and w and x:
            perm_str = u'ALL'

        pem['permission'] = perm_str
        return pem

    @classmethod
    def from_text_pem(cls, pem):
        acl = {"username": pem.get('username')}
        permission = pem.get('permission').upper()
        perm_dict = {'read': False, 'write': False, 'execute': False}

        if u'ALL' in permission:
            perm_dict = {'read': True, 'write': True, 'execute': True}
        elif u'NONE' in permission:
            perm_dict = {'read': False, 'write': False, 'execute': False}
        else:
            if u'READ' in permission:
                perm_dict['read'] = True
            if u'WRITE' in permission:
                perm_dict['write'] = True
                perm_dict['read'] = True
            if u'EXECUTE' in permission:
                perm_dict['execute'] = True
                perm_dict['read'] = True
        acl['permission'] = perm_dict
        return acl

    @classmethod
    def validate_acl(cls, acl, permissive=False):
        """
        Validate an ACL object as a dict

        Failure raises Exception unless permissive is True
        * Does not validate that username exists
        """
        err = 'Invalid ACL: {}'
        try:
            assert isinstance(acl, dict), "Not a dict"
            assert 'username' in acl and 'permission' in acl, \
                "Both username and permission are required"
            assert isinstance(acl['permission'], dict), \
                "Permission must be a dict"
            assert isinstance(acl['username'], basestring), \
                "Username must be string or unicode"
            assert set(acl['permission'].keys()) == set(VALID_PEMS) or \
                set(acl['permission'].keys()) <= set(VALID_PEMS), \
                "Valid permission types are {} not {}".format(
                    VALID_PEMS, list(acl['permission'].keys()))
            for p in acl['permission']:
                assert isinstance(acl['permission'][p], bool), \
                    "Only Boolean values allowed for permission values"
            return True
        except Exception as exc:
            if permissive is True:
                return False
            else:
                raise AgaveError(err.format(exc))


    def __get_api_username(self):
        '''Determine username'''
        if os.environ.get('_abaco_username'):
            return os.environ.get('_abaco_username')
        elif self.client.username is not None:
            return self.client.username
        else:
            raise AgaveError("No username could be determined")

    def __get_api_token(self):
        '''Determine API access_token'''
        if os.environ.get('_abaco_access_token'):
            return os.environ.get('_abaco_access_token')
        elif self.client.token.token_info.get('access_token') is not None:
            return self.client.token.token_info.get('access_token')
        else:
            raise AgaveError("Failed to retrieve API access_token")

    def __get_api_server(self):
        '''Determine API server'''
        if os.environ.get('_abaco_api_server'):
            return os.environ.get('_abaco_api_server')
        elif self.client.token.api_server is not None:
            return self.client.token.api_server
        else:
            return 'https://api.sd2e.org'
