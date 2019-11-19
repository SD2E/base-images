from __future__ import absolute_import

from . import agaveutils, aliases, logtypes,\
    jsonmessages, process, storage, uniqueid
"""
Utility library for building TACC Reactors
"""

import datetime
import json
import os
import petname
import pytz
import re
import sys
import validators
import requests

from time import sleep, time
from random import random

from attrdict import AttrDict
from agavepy.agave import Agave, AgaveError
from agavepy.actors import get_context
from agavepy.actors import get_client
from requests.exceptions import HTTPError

# config library - replaces legacy config.py
from tacconfig import config

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_LOCS = [HERE, '/', os.getcwd()]
sys.path.insert(0, os.path.dirname(HERE))
sys.path.append(os.path.split(os.getcwd())[0])
# print("sys_path: {}".format(sys.path))
# sys.path.append('/reactors')
# from . import agaveutils, alias, logs,\
#     loggers, jsonmessages, process, storage, uniqueid

VERSION = '0.6.6'
LOG_LEVEL = 'DEBUG'
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
                    '_event_uuid': 'x_session'}

ABACO_VARS_MAP = {'content_type': '_abaco_Content-Type',
                  'execution_id': '_abaco_execution_id',
                  'username': '_abaco_username',
                  'state': '_abaco_actor_state',
                  'actor_dbid': '_abaco_actor_dbid',
                  'actor_id': '_abaco_actor_id',
                  'raw_message': 'MSG'}


def get_client_with_mock_support():
    '''
    Get the current Actor API client

    Returns the Abaco actor's client if running deployed. Attempts to
    bootstrap a client from supplied credentials if running in local or
    debug mode.
    '''
    client = None
    if '_abaco_access_token' not in os.environ:
        try:
            client = Agave.restore()
        except TypeError as err:
            raise AgaveError('Unable to restore Agave client: {}'.format(err))
    else:
        try:
            client = get_client()
        except Exception as err:
            raise AgaveError('Unable to get Agave client from context: {}'.format(err))

    return client


def get_context_with_mock_support(agave_client):
    '''
    Return the current Actor context

    Return the Abaco actor's environment context if running deployed. Creates
    a test context based on inferred or mocked values if running in local or
    debug mode.
    '''
    _context = get_context()
    if os.environ.get('_abaco_actor_id') is None:
        _phony_actor_id = uniqueid.get_id()
        _phony_exec_id = uniqueid.get_id()
        _username = os.environ.get('_abaco_username', None)
        if _username is None:
            try:
                _username = agave_client.username
            except Exception:
                pass

        __context = AttrDict({'raw_message': os.environ.get('MSG', ''),
                              'content_type': 'application/json',
                              'username': _username,
                              'actor_dbid': _phony_actor_id,
                              'actor_id': _phony_actor_id,
                              'execution_id': _phony_exec_id,
                              'state': {}})
        # Merge new values from __context
        _context = _context + __context
        # Update environment
        set_os_environ_from_mock(__context)
        set_os_environ_from_client(agave_client)
    return AttrDict(_context)


def get_token_with_mock_support(client):
    '''Find current Oauth2 access token from context or mock'''
    token = None
    try:
        token = os.environ.get('_abaco_access_token', None)
    except Exception:
        pass
    if token is not None and token != '':
        try:
            token = client._token
        except Exception:
            pass
    return token


def set_os_environ_from_mock(context):
    '''Set environment vars to mocked values'''
    if context is None:
        context = {}
    try:
        for (env_k, env_v) in context.items():
            abenv = ABACO_VARS_MAP[env_k]
            os.environ[abenv] = str(env_v)
    except Exception:
        pass
    return True


def set_os_environ_from_client(agave_client):
    '''Set environment vars to client values'''
    try:
        os.environ['_abaco_api_server'] = agave_client.api_server
    except Exception:
        pass
    try:
        os.environ['_abaco_access_token'] = agave_client._token
    except Exception:
        pass
    return True


def read_config(namespace=NAMESPACE, places_list=CONFIG_LOCS,
                update=True, env=True):
    """Override tacconfig's broken right-favoring merge"""
    master_config = None
    for place in places_list:
        new_config = config.read_config(namespace=namespace,
                                        places_list=[place],
                                        env=env)
        if isinstance(new_config, dict) and master_config is None:
            master_config = new_config.copy()
        master_config = master_config + new_config
    return master_config


def microseconds():
    return int(round(time() * 1000 * 1000))


class Reactor(object):
    """
    Helper class providing a client-side API for the Actors service
    """

    def __init__(self, redactions=[]):
        self.nickname = petname.Generate(2, '-')
        self.client = get_client_with_mock_support()
        self.context = get_context_with_mock_support(agave_client=self.client)
        self._token = get_token_with_mock_support(self.client)
        self.uid = self.context.get('actor_id')
        self.execid = self.context.get('execution_id')
        self.state = self.context.get('state')
        self.worker_id = os.environ.get('_abaco_worker_id', None)
        self.container_repo = os.environ.get('_abaco_container_repo', None)
        self.actor_name = os.environ.get('_abaco_actor_name', None)
        self.created = microseconds()
        self.aliases = aliases.store.AliasStore(self.client,
                                                aliasPrefix='v1-alias-')
#        self.aliascache = {}
        self.loggers = AttrDict({'screen': None, 'slack': None})
        self.pemagent = agaveutils.recursive.PemAgent(self.client)

        # A session in the Reactors context is a linked set of executions
        # that inherit an identifier from their parent. If a reactor doesn't
        # detect a session on init, it creates one from its nickname.
        self.session = self.context.get('x_session',
                                        self.context.get(
                                            'SESSION',
                                            self.nickname))

        # Abaco injects the requester's username into context. If it's not
        # present, we assume the code is running under local emulation or j
        # inside a unit test. Bootstrap by polling the profiles
        # service to get username, a slow but reliabe operation.
        _username = self.context.get('username', None)
        if (_username is None) or (_username == ''):
            try:
                # In testing mode, username is a private attribute of client
                _username = self.client.profiles.get()['username']
            except Exception:
                _username = 'none'
        self.username = _username

        # Used by reactor implemetors to build conditionals for local testing
        localonly = str(os.environ.get('LOCALONLY', 0))
        if localonly == '1':
            self.local = True
        else:
            self.local = False

        # Bootstrap configuration via tacconfig module
        self.settings = read_config(namespace=NAMESPACE,
                                    places_list=CONFIG_LOCS,
                                    update=True,
                                    env=True)

        # Build up a list of text strings to redact in logs. We start with
        # redaction passed at init, then append values of any varable passed
        # as a tacconfig environment variable override. The assumption is that
        # such variables are probably sensitive if not outright secret and
        # should thus not be easily discoverable.
        #
        # TODO - Integrate this with the eventual TACC secrets API
        # TODO - Break out into a function to support unit testing
        envstrings = []
        if len(redactions) > 0 and isinstance(redactions, list):
            envstrings = redactions
        # The Oauth access token
        try:
            if len(self._token) > 3:
                envstrings.append(self._token)
        except Exception:
            pass
        # Add nonce values to the redact list
        envstrings.extend(self._get_nonce_vals())
        # Pull in taccconfig environment overrides
        try:
            env_config_vals = config.get_env_config_vals(namespace=NAMESPACE)
        except Exception:
            env_config_vals = []
        envstrings.extend(env_config_vals)
        # remove duplicates
        envstrings = list(set(envstrings))

        # Set up loggers

        # Dict of fields that we want to send with each logstash
        # structured log response
        extras = {'agent': self.uid,
                  'task': self.execid,
                  'name': self.actor_name,
                  'username': self.username,
                  'session': self.session,
                  'resource': self.container_repo,
                  'subtask': self.worker_id,
                  'host_ip': requests.request('GET', 'http://myip.dnsomatic.com').text
                  }

        # Screen logger prints to the following, depending on configuration
        # STDERR - Always
        # FILE   - If log_file is provided
        # AGGREGATOR - If log_token is provided
        self.loggers.screen = logtypes.get_screen_logger(
            self.uid,
            self.execid,
            settings=self.settings,
            redactions=envstrings,
            fields=extras)

        # assuming either env or config.yml is set up
        # correctly, post messages from here to Slack
        self.loggers.slack = logtypes.get_slack_logger(
            self.uid, 'slack', settings=self.settings,
            redactions=envstrings)

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

        # Temporary hack
        #
        # Avoid the call to /actors/:actorId if
        # possible, since it DDOSes the service under load. Also
        # the name will soon be avaiable in reactor context as per
        # https://github.com/TACC/abaco/issues/53
        if attribute == 'name':
            if os.environ.get('_abaco_actor_name', None) is not None:
                return os.environ.get('_abaco_actor_name')

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
        """
        Log message and exit 0
        """
        self.logger.info(successMessage)
        sys.exit(0)

    def on_failure(self, failMessage="Failure", exceptionObject=None):
        """
        Log message and exit 0
        """
        self.logger.critical("{} : {}".format(
            failMessage, exceptionObject))
        sys.exit(1)

    def _make_sender_tags(self, senderTags=True):
        """
        Internal function for capturing actor and app provenance attributes
        """
        sender_envs = {}
        if senderTags is True:
            for env in list(SPECIAL_VARS_MAP.keys()):
                if os.environ.get(env):
                    sender_envs[SPECIAL_VARS_MAP[env]] = os.environ.get(env)

        if 'x_session' not in sender_envs:
            sender_envs['x_session'] = self.session
        return sender_envs

    def _get_environment(self, passed_envs={},
                         sender_envs={}, senderTags=True):
        """
        Private method to merge user- and platform-specific environments
        """
        env_vars = passed_envs
        sender_envs = self._make_sender_tags(senderTags)
        env_vars.update(sender_envs)
        return env_vars

    def resolve_actor_alias(self, alias):
        """
        Look up the identifier for a alias string

        Arguments
            alias (str): An alias, actorId, appId, or the me/self shortcut

        Returns:
            str: The resolved identifier

        On error:
        Returns value of text

        Note:
            Does basic optimization of returning an app ID or abaco actorId
            if they are passed, as we can safely assume those are not aliases.
        """

        # Optimizations
        if alias.lower() in ['me', 'self']:
            return self.uid
        if uniqueid.is_hashid(alias):
            return alias
        # No longer supported!
        # if agaveutils.entity.is_appid(alias):
        #     return alias

        # Consult linked_reactors stanza in config.yml. This allows Reactor-
        # scoped override of aliases defined by the Abaco service
        try:
            # file:config.yml
            # ---
            # linked_reactors:
            #   <aliasName:str>:
            #       id: <actorId:str>
            #       options: <dict>
            identifier = self.settings.get('linked_reactors', {}).get(alias, {}).get('id', None)
            if identifier is not None and isinstance(identifier, str):
                return identifier
        except KeyError:
            pass

        # Resolution has not failed but rather has identified a value that is
        # likely to be an Abaco platform alias
        return alias

    def send_message(self, actorId, message,
                     environment={}, ignoreErrors=True,
                     senderTags=True, retryMaxAttempts=MAX_RETRIES,
                     retryDelay=1, sync=False):
        """
        Send a message to an Abaco actor by ID, platform alias, or defined alias

        Arguments:
            actorId (str): An actorId or alias
            message (str/dict) : Message to send

        Keyword Arguments:
            ignoreErrors: bool -  only mark failures by logging not exception
            environment: dict - environment variables to pass as url params
            senderTags: bool - send provenance and session vars along
            retryDelay: int - seconds between retries on send failure
            retryMax: int - number of times (up to global MAX_RETRIES) to retry
            sync: bool - not implemented - wait for message to execute

        Returns:
            str: The excecutionId of the resulting execution

        Raises:
            AgaveError: Raised if ignoreErrors is True
        """

        # Build dynamic list of variables. This is how attributes like
        # session and sender-id are propagated
        environment_vars = self._get_environment(environment, senderTags)
        resolved_actor_id = self.resolve_actor_alias(actorId)

        retry = retryDelay
        attempts = 0
        execution_id = None
        exceptions = []
        noexecid_err = 'Response received from {} but no executionId was found'
        exception_err = 'Exception encountered messaging {}'
        terminal_err = 'Message to {} failed after {} tries with errors: {}'

        self.logger.info("Message.to: {}".format(actorId))
        self.logger.debug("Message.body: {}".format(message))

        while attempts <= retryMaxAttempts:
            try:
                response = self.client.actors.sendMessage(
                    actorId=resolved_actor_id,
                    body={'message': message},
                    environment=environment_vars)

                if 'executionId' in response:
                    execution_id = response.get('executionId')
                    if execution_id is not None:
                        return execution_id
                    else:
                        self.logger.error(
                            noexecid_err.format(resolved_actor_id))
                else:
                    self.logger.error(
                        noexecid_err.format(resolved_actor_id))

            except HTTPError as herr:
                if herr.response.status_code == 404:
                    # Agave never returns 404 unless the thing isn't there
                    # so might as well bail out early if we see one
                    attempts = retryMaxAttempts + 1
                else:
                    http_err_resp = agaveutils.process_agave_httperror(herr)
                    self.logger.error(http_err_resp)

            # This should only happen in egregious circumstances
            # since the vast majority of AgavePy error manifest as
            # a requests HTTPError
            except Exception as e:
                exceptions.append(e)
                self.logger.error(exception_err.format(resolved_actor_id))

            attempts = attempts + 1
            # random-skew exponential backoff with limit
            if attempts <= retryMaxAttempts:
                self.logger.debug('pause {} sec then try again'.format(retry))
                sleep(retry)
                retry = retry * (1.0 + random())
                if retry > 32:
                    retry = 32

        # Maximum attempts have passed and execution_id was not returned
        if ignoreErrors:
            self.logger.error(terminal_err.format(resolved_actor_id,
                                                  retryMaxAttempts,
                                                  exceptions))
        else:
            raise AgaveError(terminal_err.format(resolved_actor_id,
                                                 retryMaxAttempts,
                                                 exceptions))

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
                                             messageschema=messageschema,
                                             permissive=permissive)

    def create_webhook(self, permission='EXECUTE', maxuses=-1, actorId=None):
        """
        Create a .actor.messages URI suitable for use in integrations

        Default is to grant EXECUTE with unlimited uses.
        """
        if actorId is not None:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            api_server = agaveutils.utils.get_api_server(self.client)
            nonce = self.add_nonce(permission,
                                   maxuses, actorId=_actorId)
            nonce_id = nonce.get('id')
            uri = '{}/actors/v2/{}/messages?x-nonce={}'.format(
                api_server, _actorId, nonce_id)
            if validators.url(uri):
                return uri
            else:
                raise ValueError("Webhook URI {} is not valid".format(uri))
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def delete_webhook(self, webhook, actorId=None):
        """
        'Delete' an actor-specific webhook by deleting its nonce

        A key assumption is that webhook was constructed by create_webhook or
        its equivalent, as this method sensitive to case and url structure
        """
        if actorId is not None:
            _actorId = actorId
        else:
            _actorId = self.uid

        # webhook must be plausibly associated with the specified actor
        if not re.search('/actors/v2/{}'.format(_actorId), webhook):
            raise ValueError("URI doesn't map to actor {}".format(_actorId))

        try:
            m = re.search('x-nonce=([A-Z0-9a-z\\.]+_[A-Z0-9a-z]+)', webhook)
            nonce_id = m.groups(0)[0]
            self.delete_nonce(nonceId=nonce_id, actorId=_actorId)
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def add_nonce(self, permission='READ', maxuses=1, actorId=None):
        """
        Add a new nonce.

        Positional arguments:
        None

        Keyword arguments:
        username: str - a valid TACC.cloud username or role account
        permission: str - a valid Abaco permission level
        maxuses: int (-1,inf) - maximum number of uses for a given nonce
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        assert permission in ('READ', 'EXECUTE', 'UPDATE'), \
            'Invalid permission: (READ, EXECUTE, UPDATE)'
        assert isinstance(maxuses, int), 'Invalid max_uses: (-1,-inf)'
        assert maxuses >= -1, 'Invalid max_uses: (-1,-inf)'
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            body = {'level': permission,
                    'maxUses': maxuses}
            resp = self.client.actors.addNonce(actorId=_actorId,
                                               body=json.dumps(body))
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def get_nonce(self, nonceId, actorId=None):
        """
        Get an specific nonce by its ID

        Positional arguments:
        nonceId: str - a valid TACC.cloud username or role account

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            resp = self.client.actors.getNonce(
                actorId=_actorId, nonceId=nonceId)
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def delete_nonce(self, nonceId, actorId=None):
        """
        Delete an specific nonce by its ID

        Positional arguments:
        nonceId: str - a valid TACC.cloud username or role account

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            resp = self.client.actors.deleteNonce(
                actorId=_actorId, nonceId=nonceId)
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def list_nonces(self, actorId=None):
        """
        List all nonces

        Positional arguments:
        None

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            resp = self.client.actors.listNonces(
                actorId=_actorId)
            return resp
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def delete_all_nonces(self, actorId=None):
        """
        Delete all nonces from an actor

        Keyword arguments:
        actorId: str - an Abaco actor ID. Defaults to self.uid if not set.
        """
        if actorId:
            _actorId = actorId
        else:
            _actorId = self.uid

        try:
            nonces = self.list_nonces(actorId=_actorId)
            assert isinstance(nonces, list)
            for nonce in nonces:
                self.delete_nonce(nonce.get('id'), actorId=_actorId)
        except HTTPError as h:
            http_err_resp = agaveutils.process_agave_httperror(h)
            raise AgaveError(http_err_resp)
        except Exception as e:
            raise AgaveError(
                "Unknown error: {}".format(e))

    def _get_nonce_vals(self):
        """
        Get nonce value from environment

        Details: Extract value of x-nonce if it was passed. This is used to
        set up redaction, but could also be used to pass the nonce along to
        another context. Currently, we only expect one nonce, but there
        could be nonces from other services so this is implemented to return
        a list of nonce values.
        """
        nonce_vals = []
        try:
            nonce_value = self.context.get('x-nonce', None)
            if nonce_value is not None:
                nonce_vals.append(nonce_value)
        except Exception:
            pass
        return nonce_vals

    def elapsed(self):
        """Returns elapsed time in microseconds since Reactor was initialized"""
        return microseconds() - self.created


def utcnow():
    '''
    Return a text-formatted UTC date

    example: 2018-01-05T18:40:55.290790+00:00
    '''
    t = datetime.datetime.now(tz=pytz.utc)
    return t.isoformat()

# Verified Py3 compatible
