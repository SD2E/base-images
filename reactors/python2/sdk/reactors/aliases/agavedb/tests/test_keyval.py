#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Usage: See bundled README.md

from builtins import str

import json
import os
import pytest
import random
import uuid

from agavepy.agave import Agave, AgaveError
from keyval import AgaveKeyValStore
import uniqueid

from . import testdata
# fixtures
from .agavefixtures import *

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='session')
def prefix():
    kvs = uniqueid.get_id()
    return kvs


@pytest.fixture(scope='session')
def keyvalstore(agave, prefix):
    kvs = AgaveKeyValStore(agave, prefix)
    return kvs

@pytest.fixture(scope='session')
def fake_key():
    return 'keyval-test-' + str(random.randint(10, 99))

@pytest.fixture(scope='session')
def fake_key_acl():
    return 'acl-test-' + str(random.randint(10, 99))

@pytest.fixture(scope='session')
def fake_user():
    return 'taco' + str(random.randint(10, 99))


@pytest.fixture(scope='session')
def fake_value():
    return uniqueid.get_id() * 5



@pytest.fixture(scope='session')
def test_data(credentials):
    return testdata.TestData(credentials).data()


def test_key_valid(keyvalstore, test_data):

    # types
    invalid_types = test_data['key_valid']['types']
    for test_key in invalid_types:
        with pytest.raises(AssertionError) as excinfo:
            keyvalstore._key_is_valid(test_key)
        assert 'string or unicode' in str(excinfo.value)

    # length check
    invalid_lengths = test_data['key_valid']['lengths']
    for test_key in invalid_lengths:
        with pytest.raises(AssertionError) as excinfo:
            keyvalstore._key_is_valid(test_key)
        assert 'length:' in str(excinfo.value)

    # non-whitespace characters
    invalid_whitespace = test_data['key_valid']['whitespace']
    for test_key in invalid_whitespace:
        with pytest.raises(AssertionError) as excinfo:
            keyvalstore._key_is_valid(test_key)
        assert 'non-whitespace characters' in str(excinfo.value)

    # banned characters
    banned_chars = test_data['key_valid']['banned']
    for test_key in banned_chars:
        with pytest.raises(AssertionError) as excinfo:
            keyvalstore._key_is_valid(test_key)
        assert 'key may not contain' in str(excinfo.value)


def test_namespace_fwd(keyvalstore, prefix, credentials):
    '''_namespace'''
    ns = keyvalstore._namespace('abc123')
    expected = prefix + '/' + 'abc123#' + credentials['username']
    assert ns == expected


def test_namespace_rev_namespace(keyvalstore, credentials, prefix):
    '''_namespace_rev'''
    # with #username extension
    ns = keyvalstore._rev_namespace(
        prefix + '/' + 'abc123#' + credentials['username'], False)
    expected = 'abc123#' + credentials['username']
    assert ns == expected


def test_namespace_rev_wo_namespace(keyvalstore, credentials, prefix):
    '''_namespace_rev'''
    # without #username extension
    ns = keyvalstore._rev_namespace(
        prefix + '/' + 'abc123#' + credentials['username'], True)
    expected = 'abc123'
    assert ns == expected


def test_value_valid_type(keyvalstore, credentials):
    '''valid values for keys'''

    # dict
    with pytest.raises(AssertionError) as excinfo:
        keyvalstore._value_is_valid({'name': 'value'})
    assert 'string or unicode' in str(excinfo.value)

    # tuple
    with pytest.raises(AssertionError) as excinfo:
        keyvalstore._value_is_valid(('new york', 'los angeles'))
    assert 'string or unicode' in str(excinfo.value)

    # list
    with pytest.raises(AssertionError) as excinfo:
        keyvalstore._value_is_valid([1, 2, 3])
    assert 'string or unicode' in str(excinfo.value)

    # NoneType
    with pytest.raises(AssertionError) as excinfo:
        keyvalstore._value_is_valid(None)
    assert 'string or unicode' in str(excinfo.value)

    # python obkect
    with pytest.raises(AssertionError) as excinfo:
        keyvalstore._value_is_valid(keyvalstore)
    assert 'string or unicode' in str(excinfo.value)


def test_set_get_rem(keyvalstore, credentials):
    '''test key set/get/delete cycle'''
    key_name = 'keyval-test-' + str(random.randint(10, 99))
    key_valu = '6edd8c34-3aba-46d8-86bf-550db9ffb909'
    set_key_name = keyvalstore.set(key_name, key_valu)
    assert set_key_name == key_name
    get_key_valu = keyvalstore.get(key_name)
    assert get_key_valu == key_valu
    assert keyvalstore.rem(key_name) is True


def test_get_nonexistent(keyvalstore, credentials):
    '''test get on a key that doesn't exist'''
    with pytest.raises(ValueError):
        key_name = uuid.uuid4().hex
        keyvalstore.get(key_name)


def test_getall(keyvalstore, credentials):
    '''getall - validate that an array is returned'''
    assert isinstance(keyvalstore.getall(), list)


def test_username(keyvalstore, credentials):
    '''verify that agavedb and test view of username is same'''
    assert credentials['username'] == keyvalstore._username()


def test_validate_acl(keyvalstore, test_data):
    '''run through various ACL forms'''
    acls = test_data.get('acls')
    # check that valid acls all pass
    for acl in acls['valid']:
        keyvalstore.validate_acl(acl, permissive=False)
    # check that invalid structs are detected
    for acl in acls['invalid']:
        with pytest.raises(AgaveError) as exc:
            keyvalstore.validate_acl(acl, permissive=False)
        assert 'Invalid ACL' in str(exc.value)
    # check that permssive squashes Exception
    for acl in acls['invalid']:
        response = keyvalstore.validate_acl(acl, permissive=True)
        assert response is False


def test_list_acl(keyvalstore, fake_key_acl, fake_value, test_data):
    fake_key = fake_key_acl
    response = keyvalstore.set(fake_key, fake_value)
    assert isinstance(keyvalstore.getacls(response), list)
    keyvalstore.rem(fake_key)


def test_add_acl(keyvalstore, fake_key_acl, fake_value, fake_user, test_data):
    fake_key = fake_key_acl
    keyvalstore.set(fake_key, fake_value)
    fake_acl = {'username': fake_user, 'permission': {'read': True}}
    assert keyvalstore.setacl(fake_key, fake_acl) is True
    resp = keyvalstore.getacls(fake_key)
    unames = []
    for acl in resp:
        unames.append(acl.get('username'))
    assert fake_user in unames, 'test user not found in listing'
    resp = keyvalstore.getacls(fake_key, user=fake_user)
    if len(resp) > 0:
        acl_read = resp[0].get('permission').get('read', False)
        acl_write = resp[0].get('permission').get('write', False)
        acl_execute = resp[0].get('permission').get('execute', False)
    else:
        acl_read, acl_write, acl_execute = False, False, False
    assert acl_read is True, 'user should be able to read'
    assert acl_write is False, 'user shouldnt be able to write'
    assert acl_execute is False, 'user shouldnt be able to exec'
    keyvalstore.rem(fake_key)


def test_acl_from_world(keyvalstore, fake_key_acl, fake_value,
                        fake_user, test_data):
    fake_key = fake_key_acl
    keyvalstore.set(fake_key, fake_value)
    fake_acl = {'username': 'world', 'permission': {'read': True}}
    assert keyvalstore.setacl(fake_key, fake_acl) is True
    resp = keyvalstore.getacls(fake_key)
    unames = []
    for acl in resp:
        unames.append(acl.get('username'))
    assert 'world' in unames, 'world user not found in listing'
    # world granted read, so fake user should be able to see it
    # this abuses the fact that the agave pems system doesnt validate unames
    resp = keyvalstore.getacls(fake_key, user=fake_user)
    if len(resp) > 0:
        acl_read = resp[0].get('permission').get('read', False)
        acl_write = resp[0].get('permission').get('write', False)
        acl_execute = resp[0].get('permission').get('execute', False)
    else:
        acl_read, acl_write, acl_execute = False, False, False
    assert acl_read is True, 'user should inherit +read'
    assert acl_write is False, 'user should not inherit +write'
    assert acl_execute is False, 'user should not inherit +exec'
    assert keyvalstore.remacl(fake_key, 'world') is True
    # Having stripped away world permission, test user should lose its ACL
    resp = keyvalstore.getacls(fake_key, user=fake_user)
    if len(resp) > 0:
        acl_read = resp[0].get('permission').get('read', False)
        acl_write = resp[0].get('permission').get('write', False)
        acl_execute = resp[0].get('permission').get('execute', False)
    else:
        acl_read, acl_write, acl_execute = False, False, False
    assert acl_read is False, 'user should no longer inherit +read'
    assert acl_write is False, 'user should not inherit +write'
    assert acl_execute is False, 'user should not inherit +exec'
    keyvalstore.rem(fake_key)

def test_remall(keyvalstore):
    '''verify that we can delete our session-specific entries'''
    db = keyvalstore.deldb()
    assert db == []
    assert isinstance(db, list)
    assert len(db) == 0
