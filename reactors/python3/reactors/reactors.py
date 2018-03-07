"""
Utility library for building TACC Reactors
"""

import os
import sys
import petname
import pytz
import datetime
from attrdict import AttrDict

from agavepy.actors import get_context
from agavepy.actors import get_client
from agavepy.actors import update_state

sys.path.insert(0, os.path.dirname(__file__))
from config import settings as settingsAttrDict
from logs import *
from uniqueid import get_id
from storage import *

VERSION = '0.5.0'

def utcnow():
    """
    Returns text-formatted
    e.g.) 2018-01-05T18:40:55.290790+00:00
    """
    t = datetime.datetime.now(tz=pytz.utc)
    return t.isoformat()


def get_client_with_mock_support():
    """
    Return the Abaco actor's API client if
    running as a function. Try to return
    user's local Agave client for debug
    and test purposes.
    """
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
    """
    Return the Abaco actor's environment
    context if running as a function. Otherwise,
    return a mock environment for debug
    and test purposes
    """
    _context = get_context()
    if os.environ.get('_abaco_actor_id') is None:
        _phony_actor_id = get_id() + '.local'
        __context = AttrDict({'raw_message': os.environ.get('MSG', ''),
                              'content_type': 'application/json',
                              'execution_id': get_id() + '.local',
                              'username': os.environ.get('_abaco_username'),
                              'state': {},
                              'actor_dbid': _phony_actor_id,
                              'actor_id': _phony_actor_id})
        # Merge new values from __context
        _context = _context + __context
    return _context


nickname = petname.Generate(3, '-')
settings = settingsAttrDict
client = get_client_with_mock_support()
context = get_context_with_mock_support()
try:
    username = client.username.encode("utf-8", "strict")
except Exception:
    username = 'unknown'
uid = context.get('actor_id')
logger = get_logger(context.get('actor_id', nickname))
