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
from time import sleep

# config library - replaces legacy config.py
from tacconfig import config

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.append(os.path.split(os.getcwd())[0])
# print("sys_path: {}".format(sys.path))
# sys.path.append('/reactors')
from reactors import agaveutils, alias, logs, jsonmessages, storage, uniqueid


VERSION = '0.6.1'
LOG_LEVEL = 'ERROR'
LOG_FILE = None
NAMESPACE = '_REACTOR'
HASH_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'
MESSAGE_SCHEMA = '/message.jsonschema'
MAX_ELAPSED = 300
MAX_RETRIES = 5
SPECIAL_VARS_MAP = {'_abaco_actor_id': 'x_src_actor_id',
                    '_abaco_execution_id': 'x_src_execution_id',
                    'APP_ID': 'x_src_app_id',
                    'JOB_ID': 'x_src_job_id',
                    'EVENT': 'x_src_event',
                    'UUID': 'x_src_uuid',
                    '_event_uuid': 'x_external_event_id'}

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
        self.aliases = alias.AliasStore(self.client)
        self.aliascache = {}

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

    def _resolve_actor_id(self, actorId):
        """Private method for looking up an Alias"""
        # Look up actorId by name. Honor special alias 'me' to allow actor
        # to message itself. Todo: Investigate whether its better/faster to
        # query /actors for actorId before invoking the alias lookup
        resolved_actor_id = None
        if actorId == 'me':
            resolved_actor_id = self.uid
            self.logger.debug("Invoked 'me' convenience alias")
        elif self.aliascache.get(actorId) is not None:
            resolved_actor_id = self.aliascache.get(actorId)
            self.logger.debug("Alias found in local cache")
        else:
            lookup = None
            try:
                lookup = self.aliases.get_name(actorId)
            except Exception as e:
                self.logger.debug("Unable to lookup {}: {}".format(actorId, e))
            if lookup is not None:
                resolved_actor_id = lookup
                self.aliascache[actorId] = lookup
            else:
                resolved_actor_id = actorId
                self.logger.debug("Giving up. It must be an actual actor ID")

        # Coerce to stringy value Py2/Py3
        if isinstance(resolved_actor_id, bytes):
            return resolved_actor_id.decode('utf-8')
        else:
            return resolved_actor_id

    def _make_sender_tags(self, senderTags=True):
        """Private method for passing along provenance variables"""
        sender_envs = {}
        if senderTags is True:
            for env in list(SPECIAL_VARS_MAP.keys()):
                if os.environ.get(env):
                    sender_envs[SPECIAL_VARS_MAP[env]] = os.environ.get(env)
        return sender_envs

    def _get_environment(self, passed_envs={},
                         sender_envs={}, senderTags=True):
        """Private method to merge user- and platform-specific envs"""
        env_vars = passed_envs
        sender_envs = self._make_sender_tags(senderTags)
        env_vars.update(sender_envs)
        return env_vars

    def send_message(self, actorId, message,
                     environment={}, ignoreErrors=True,
                     senderTags=True, retryMaxAttempts=MAX_RETRIES,
                     retryDelay=30, sync=False):
        """
        Send a message to an Abaco actor by its alias or ID

        Positional parameters:
        actorId - str - Valid actorId or alias
        message - str/dict - Message to send

        Keyword arguments:
        ignoreErrors - bool -  only mark failures by logging not exception
        retryDelay - int - seconds between retries on send failure
        retryMax  - int - number of times (up to global MAX_RETRIES) to resend
        environment - dict - environment variables to pass as url params
        sync - not implemented
        senderTags - not implemented

        Returns
        Execution ID as str

        If ignoreErrors is True, this is a fire-and-forget operation. Else,
        failures raise an Exception to handled by the caller.
        """

        environment_vars = self._get_environment(environment, senderTags)
        resolved_actor_id = self._resolve_actor_id(actorId)

        message_was_successful = False
        execution_id = None
        attempts = 0
        exceptions = []

        while message_was_successful is False and attempts <= retryMaxAttempts:

            try:

                self.logger.debug("Destination: {}".format(actorId))
                self.logger.debug("Body: {}".format(message))
                self.logger.debug("Env: {}".format(environment_vars))

                response = self.client.actors.sendMessage(
                    actorId=resolved_actor_id,
                    body={'message': message},
                    environment=environment_vars)

                self.logger.debug("Response: {}".format(response))

                execution_id = response.get('executionId', None)
                message_was_successful = True
            except Exception as e:
                exceptions.append(e)
                attempts = attempts + 1
                if MAX_RETRIES > 1:
                    self.logger.warning(
                        "Retrying message to {}".format(actorId))
                    sleep(retryDelay)

        if execution_id is None:
            error_message = "Message to {} failed with " + \
                "Exception(s): {}".format(actorId, exceptions)
            self.logger.error(error_message)
            if ignoreErrors:
                pass
            else:
                raise Exception(error_message)

        return execution_id

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
