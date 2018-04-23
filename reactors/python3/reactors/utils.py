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
# from . import agaveutils, alias, logs,\
#     loggers, jsonmessages, process, storage, uniqueid
from . import agaveutils, alias, logtypes,\
    jsonmessages, process, storage, uniqueid

VERSION = '0.6.2'
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
        self.nickname = petname.Generate(2, '-')
        self.context = get_context_with_mock_support()
        self.client = get_client_with_mock_support()
        self.uid = self.context.get('actor_id')
        self.execid = self.context.get('execution_id')
        self.state = self.context.get('state')
        self.aliases = alias.AliasStore(self.client)
        self.aliascache = {}
        self.loggers = AttrDict({'screen': None, 'slack': None})
        self.pemagent = agaveutils.recursive.PemAgent(self.client)

        # Used by reactor implemetors to build conditionals for local testing
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

        # Bootstrap configuration via tacconfig module
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

        # Set up multiple logger instances
        # stderr is the basic print-to-screen logger
        self.loggers.screen = logtypes.get_screen_logger(
            self.uid, self.execid, log_level=log_level,
            log_file=log_file, redactions=envstrings)

        # assuming either env or config.yml is set up
        # correctly, post messages from here to Slack
        self.loggers.slack = logtypes.get_slack_logger(
            self.uid, 'slack', self.settings.slack,
            log_level=log_level, redactions=envstrings)

        # Alias to stderr logger so that r.logger continues to work
        self.logger = self.loggers.screen

    def get_attr(self, attribute=None, actorId=None):
        """Retrieve dict of attributes for an actor

        Parameters:
        attribute - str - Any top-level key in the Actor API model
        actorId   - str - Which actor (if not self) to fetch. Defaults to
                          the actor's own ID, allowing introspection.
        """
        default_attr = None
        default_dict = {}
        if self.local is True:
            default_attr = 'mockup'
            default_dict = {}

        if actorId is None:
            fetch_id = self.uid
        else:
            fetch_id = actorId
        try:
            myself = self.client.actors.get(actorId=fetch_id)
            if attribute is None:
                return myself
            else:
                return myself.get(attribute, default_attr)
        except Exception:
            if actorId is None and attribute is None:
                return default_dict
            else:
                return default_attr

    def on_success(self, successMessage="Success"):
        '''Log message and exit 0'''
        self.logger.info(successMessage)
        sys.exit(0)

    def on_failure(self, failMessage="Failure", exceptionObject=None):
        '''Log message and exception and exit 1'''
        self.logger.critical("{} : {}".format(
            failMessage, exceptionObject))
        sys.exit(1)

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
                     retryDelay=5, sync=False):
        """
        Send a message to an Abaco actor by ID

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
        resolved_actor_id = actorId

        message_was_successful = False
        execution_id = None
        attempts = 0
        exceptions = []

        while message_was_successful is False and attempts <= retryMaxAttempts:

            try:

                self.logger.debug("Destination: {}".format(actorId))
                self.logger.debug("Body: {}".format(message))
                self.logger.debug("Env: {}".format(environment_vars))

                # Temporarily not sending senderTags and environment due to
                # agavepy writing wrong URL construct
                # gO0JeWaBM4p3J/messages?environment=x_src_execution_id&
                #    environment=x_src_actor_id&x_src_execution_id=
                #    wa8P7jyJorRDq&x_src_actor_id=wZX5A5LgaY601
                #
                # essentially, duplicate empty vars are killing it
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
                        "Retrying message to {} (Error: {})".format(
                            actorId, e))
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