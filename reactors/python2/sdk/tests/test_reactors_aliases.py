from __future__ import print_function
from __future__ import absolute_import
from future.standard_library import install_aliases
install_aliases()

import os
import sys
import petname
import re
import pytest
from past.builtins import basestring

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
from reactors.uniqueid import get_id
from reactors.utils import Reactor


@pytest.fixture(scope='session')
def fake_version():
    return u'1.0.0'


@pytest.fixture(scope='session')
def fake_alias():
    return petname.Generate(2, '-')


@pytest.fixture(scope='session')
def fake_alias_versioned(fake_alias, fake_version):
    return fake_alias + ':' + fake_version


@pytest.fixture(scope='session')
def fake_alias_prefixed(fake_alias):
    return 'v1-alias-' + fake_alias


@pytest.fixture(scope='session')
def fake_alias_versioned_prefixed(fake_alias_prefixed, fake_version):
    return fake_alias_prefixed + ':' + fake_version


@pytest.fixture(scope='session')
def fake_actor_id():
    return get_id()


def test_createkey(fake_alias, fake_alias_prefixed):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    new_alias = r.aliases._createkey(fake_alias)
    assert new_alias in fake_alias_prefixed


def test_set(fake_alias, fake_alias_prefixed, fake_actor_id):
    r = Reactor()
    response = r.aliases.set_alias(
        alias=fake_alias, name=fake_actor_id)
    assert response in fake_alias_prefixed
    assert isinstance(response, basestring)


def test_get(fake_alias, fake_actor_id):
    r = Reactor()
    response = r.aliases.get_name(alias=fake_alias)
    assert response in fake_actor_id
    assert isinstance(response, basestring)


def test_get_me(monkeypatch, fake_alias, fake_actor_id):
    monkeypatch.setenv('_abaco_actor_id', fake_actor_id)
    r = Reactor()
    actor_id = r.uid
    assert actor_id in fake_actor_id
    response = r.aliases.get_name(alias='me')
    assert response in fake_actor_id
    assert isinstance(response, basestring)
    response = r.aliases.get_name(alias=u'me')
    assert response in fake_actor_id
    assert isinstance(response, basestring)


def test_get_aliases(fake_alias, fake_actor_id):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    r.aliases.set_alias(fake_alias, fake_actor_id)
    aliases = r.aliases.get_aliases()
    assert isinstance(aliases, list)
    assert isinstance(fake_alias, basestring)
    for test_alias in aliases:
        assert isinstance(test_alias, basestring)
    assert set([fake_alias]).issubset(set(aliases))
    # assert (set(aliases) == set([fake_alias])) or \
    #     (set[fake_alias] in set(aliases))


def test_rem(fake_alias):
    r = Reactor()
    response = r.aliases.rem_alias(alias=fake_alias)
    assert response is True
