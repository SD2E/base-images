"""
Utility library for building TACC Reactors
"""
from __future__ import absolute_import

import json
import os
import sys
import petname
import pytz
import datetime

from attrdict import AttrDict
from agavepy.actors import get_context
from agavepy.actors import get_client

# config library - replaces legacy config.py
from tacconfig import config

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.append(os.path.split(os.getcwd())[0])
# print("sys_path: {}".format(sys.path))
# sys.path.append('/reactors')
from reactors import agaveutils, aliases, logs, jsonmessages, storage, uniqueid


VERSION = '0.6.1'
LOG_LEVEL = 'ERROR'
LOG_FILE = None
NAMESPACE = '_REACTOR'
HASH_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'
MESSAGE_SCHEMA = '/message.jsonschema'

# client = None
# context = None
# nickname = None
# settings = None
# uid = None
# username = None

global client
global context
global nickname
global settings
global uid
global username


def get_client_with_mock_support():
    '''
    Get the current Actor API client

    Returns the Abaco actor's client if running deployed. Attempts to
    bootstrap a client from supplied credentials if running in local or
    debug mode.
    '''
    _client = None
    if os.environ.get('_abaco_access_token') is None:
        from agavepy.agave import Agave
        try:
            _client = Agave.restore()
        except TypeError:
            _client = None
    else:
        _client = get_client()

    return _client


def get_context_with_mock_support():
    '''
    Return the current Actor context

    Return the Abaco actor's environment context if running deployed. Creates
    a test context based on inferred or mocked values if running in local or
    debug mode.
    '''
    _context = get_context()
    if os.environ.get('_abaco_actor_id') is None:
        _phony_actor_id = uniqueid.get_id()
        __context = AttrDict({'raw_message': os.environ.get('MSG', ''),
                              'content_type': 'application/json',
                              'execution_id': uniqueid.get_id(),
                              'username': os.environ.get('_abaco_username'),
                              'state': {},
                              'actor_dbid': _phony_actor_id,
                              'actor_id': _phony_actor_id})
        # Merge new values from __context
        _context = _context + __context
    return _context


class Reactor(object):
    def __init__(self):
        '''Initialize class with a valid Agave API client'''
        self.nickname = petname.Generate(3, '-')
        self.context = get_context_with_mock_support()
        self.client = get_client_with_mock_support()
        self.uid = self.context.get('actor_id')
        self.execid = self.context.get('execution_id')
        self.state = self.context.get('state')

        localonly = str(os.environ.get('LOCALONLY', 0))
        if localonly == '1':
            self.local = True
        else:
            self.local = False

        try:
            self.username = self.client.username.encode("utf-8", "strict")
        except Exception:
            self.username = 'unknown'
            pass

        # bootstrap configuration via tacconfig module
        self.settings = config.read_config(namespace=NAMESPACE)

        # list of text strings to redact in all logs - in this case, all
        # variables passed in as env overrides since we assume those are
        # intended to be secret (or at least not easily discoverable).
        try:
            envstrings = config.get_env_config_vals(namespace=NAMESPACE)
        except Exception:
            envstrings = []

        # add in nonce to the redact list via some heuristic measures
        envstrings.extend(self._get_nonce_vals())

        # Set up logging
        #
        # Get logging level
        log_level = LOG_LEVEL
        try:
            _log_level = self.settings.get('logs').get('level')
            if isinstance(_log_level, str):
                log_level = _log_level
        except Exception:
            pass
        # Optional log file (relative to cwd())
        log_file = LOG_FILE
        try:
            _log_file = self.settings.get('logs').get('file')
            if isinstance(_log_file, str):
                log_file = _log_file
        except Exception:
            pass
        # Use 'redactions' from above to define a banlist of strings
        #   These will be replaced with * characters in all logs
        self.logger = logs.get_logger(self.uid,
                                      self.execid,
                                      log_level=log_level,
                                      log_file=log_file,
                                      redactions=envstrings)

    def on_success(self, successMessage="Success"):
        '''Log message and exit 0'''
        self.logger.info(successMessage)
        sys.exit(0)

    def on_failure(self, failMessage="Failure", exceptionObject=None):
        '''Log message and exception and exit 1'''
        self.logger.critical("{} : {}".format(
            failMessage, exceptionObject))
        sys.exit(1)

    @classmethod
    def get_client_with_mock_support():
        '''
        Get the current Actor API client

        Returns the Abaco actor's client if running deployed. Attempts to
        bootstrap a client from supplied credentials if running in local or
        debug mode.
        '''
        _client = None
        if os.environ.get('_abaco_access_token') is None:
            from agavepy.agave import Agave
            try:
                _client = Agave.restore()
            except TypeError:
                _client = None
        else:
            _client = get_client()

        return _client

    @classmethod
    def get_context_with_mock_support():
        '''
        Return the current Actor context

        Return the Abaco actor's environment context if running deployed.
        Creates a test context based on inferred or mocked values if running
        in local or debug mode.
        '''
        _context = get_context()
        if os.environ.get('_abaco_actor_id') is None:
            _phony_actor_id = uniqueid.get_id() + '.local'
            __context = AttrDict({'raw_message': os.environ.get('MSG', ''),
                                  'content_type': 'application/json',
                                  'execution_id': uniqueid.get_id() + '.local',
                                  'username': os.environ.get(
                                  '_abaco_username'),
                                  'state': {},
                                  'actor_dbid': _phony_actor_id,
                                  'actor_id': _phony_actor_id})
            # Merge new values from __context
            _context.update(__context)
        return _context

    def _get_nonce_vals(self):
        '''Fetch x-nonce if it was passed. Used to set up redaction.'''
        nonce_vals = []
        try:
            nonce_value = self.context.get('x-nonce', None)
            if nonce_value is not None:
                nonce_vals.append(nonce_value)
        except Exception:
            pass
        return nonce_vals

    def validate_message(self,
                         messagedict,
                         messageschema=MESSAGE_SCHEMA,
                         permissive=True):
        """
        Validate dictonary derived from JSON against a JSON schema

        Positional arguments:
        messagedict - dict - JSON-derived object

        Keyword arguments:
        messageschema - str - path to the requisite JSON schema file
        permissive - bool - swallow validation errors [True]
        """
        return jsonmessages.validate_message(messagedict,
                                             messageschema=MESSAGE_SCHEMA,
                                             permissive=permissive)


def utcnow():
    '''
    Return a text-formatted UTC date

    example: 2018-01-05T18:40:55.290790+00:00
    '''
    t = datetime.datetime.now(tz=pytz.utc)
    return t.isoformat()

# Verified Py3 compatible
