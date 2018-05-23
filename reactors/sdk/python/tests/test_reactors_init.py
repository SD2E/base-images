from __future__ import unicode_literals
import os
import sys

from attrdict import AttrDict
from agavepy.agave import Agave
from builtins import str
from logging import Logger

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
import pytest
from reactors.utils import Reactor


def test_init():
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    assert r.uid is not None
    assert r.execid is not None
    assert r.state is not None
    assert isinstance(r.local, bool)
    assert isinstance(r.context, AttrDict)
    assert isinstance(r.state, dict)
    assert isinstance(r.client, Agave)
    assert isinstance(r.logger, Logger)


def test_localonly_true(monkeypatch):
    '''Check LOCALONLY x Reactor.local set -> True'''
    monkeypatch.setenv('LOCALONLY', 1)
    r = Reactor()
    rlocal = r.local
    assert rlocal is True


def test_localonly_false(monkeypatch):
    '''Check LOCALONLY x Reactor.local unset -> False'''
    monkeypatch.setenv('LOCALONLY', None)
    r = Reactor()
    rlocal = r.local
    assert rlocal is False


def test_username_from_env(monkeypatch):
    '''Can we pick up username from ENV'''
    monkeypatch.setenv('_abaco_username', 'taco')
    assert '_abaco_username' in os.environ
    r = Reactor()
    assert 'username' in r.context
    r_uname = r.username
    assert r_uname == 'taco'


def test_username_from_client():
    '''Can we pick up username from Agave.client'''
    from agavepy.agave import Agave
    ag = Agave.restore()
    local_uname = ag.profiles.get()['username']
    r = Reactor()
    assert local_uname == r.username
