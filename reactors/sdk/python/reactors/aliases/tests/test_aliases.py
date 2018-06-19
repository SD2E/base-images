from __future__ import print_function
from __future__ import absolute_import
from future.standard_library import install_aliases
install_aliases()

import os
import sys
import petname
import re
import random
import uuid
from past.builtins import basestring

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.insert(0, HERE)
import pytest
from agavefixtures import credentials, agave

# module-specific classes and methods
from store import AliasStore, AgaveError, get_id


@pytest.fixture(scope='session')
def prefix():
    kvs = get_id()
    return kvs


@pytest.fixture(scope='session')
def alias_store(agave, prefix):
    kvs = AliasStore(agave, prefix)
    return kvs


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
    return 'test-alias-' + fake_alias


@pytest.fixture(scope='session')
def fake_alias_versioned_prefixed(fake_alias_prefixed, fake_version):
    return fake_alias_prefixed + ':' + fake_version


@pytest.fixture(scope='session')
def fake_actor_id():
    return get_id()


@pytest.fixture(scope='session')
def fake_app_id():
    appname = get_id()
    semver = []
    for n in range(0, 3):
        semver.append(str(int(random.random() * 100)))
    appvers = '.'.join(semver)
    return appname + '-' + appvers


def test_alias_store(alias_store):
    assert alias_store.prefix is not None


def test_createkey(alias_store, fake_alias, fake_alias_prefixed):
    '''Ensure various properties are present and the right class'''

    new_alias = alias_store._createkey(fake_alias)
    assert new_alias in fake_alias_prefixed


def test_set(alias_store, fake_alias, fake_alias_prefixed, fake_actor_id):

    response = alias_store.set_alias(
        alias=fake_alias, name=fake_actor_id)
    assert response in fake_alias_prefixed
    assert isinstance(response, basestring)


def test_get_aliases(alias_store, fake_alias, fake_actor_id):
    '''Ensure we get a list of aliases on query'''
    alias_store.set_alias(fake_alias, fake_actor_id)
    aliases = alias_store.get_aliases()
#    assert aliases == 'moof'
    assert isinstance(aliases, list)
    assert isinstance(fake_alias, basestring)
    for test_alias in aliases:
        assert isinstance(test_alias, basestring)
    assert set([fake_alias]).issubset(set(aliases)) or \
        set([fake_alias]) == set(aliases)


def test_get_name(alias_store, fake_alias, fake_actor_id):
    '''General test of get_name'''
    response = alias_store.get_name(alias=fake_alias)
    assert response in fake_actor_id
    assert isinstance(response, basestring)


def test_get_name_non_existent(alias_store):
    '''Test get on non-existent alias'''
    non_existent_alias = uuid.uuid4().hex
    with pytest.raises(ValueError):
        alias_store.get_name(alias=non_existent_alias)


@pytest.mark.parametrize("alias", [
    ("me"),
    ("self")
])
def test_actor_get_name_me(alias, alias_store, fake_actor_id, monkeypatch):
    '''Test get_name "me/self" alias for actors'''
    monkeypatch.setenv('_abaco_actor_id', fake_actor_id)
    name = alias_store.get_name(alias)
    assert name == fake_actor_id


@pytest.mark.parametrize("alias", [
    ("me"),
    ("self")
])
def test_app_get_name_me(alias, alias_store, fake_app_id, monkeypatch):
    '''gTest get_name "me/self" alias for apps'''
    monkeypatch.setenv('AGAVE_APP_ID', fake_app_id)
    name = alias_store.get_name(alias)
    assert name == fake_app_id


@pytest.mark.parametrize("alias", [
    ("me"),
    ("self")
])
def test_precedence_get_name_me(alias_store, fake_actor_id,
                                alias, monkeypatch):
    '''Test precedence for me/self: actorId >> appId'''
    monkeypatch.setenv('AGAVE_APP_ID', fake_app_id)
    monkeypatch.setenv('_abaco_actor_id', fake_actor_id)
    name = alias_store.get_name(alias)
    assert name == fake_actor_id


def test_rem_alias(alias_store, fake_alias):
    response = alias_store.rem_alias(alias=fake_alias)
    assert response is True


def test_set_unicode_alias(alias_store, fake_alias,
                           fake_alias_prefixed, fake_actor_id):

    '''be sure we can accept unicode alias'''
    unicode_fake_alias = py23_str_to_utf8(fake_alias)
    response = alias_store.set_alias(
        alias=unicode_fake_alias, name=fake_actor_id)
    assert response in fake_alias_prefixed
    assert isinstance(response, basestring)


def test_set_unicode_value(alias_store, fake_alias,
                           fake_alias_prefixed, fake_actor_id):

    '''be sure we can accept unicode value'''
    unicode_fake_actor_id = py23_str_to_utf8(fake_actor_id)
    response = alias_store.set_alias(
        alias=fake_alias, name=unicode_fake_actor_id)
    assert response in fake_alias_prefixed
    assert isinstance(response, basestring)


def test_rem_all_aliases(alias_store, fake_alias):
    response = alias_store.deldb()
    assert response == []


def py23_str_to_utf8(text):
    unicode_text = text
    try:
        unicode_text = text.decode('utf-8', 'ignore')
        return unicode_text
    except Exception:
        return unicode_text
