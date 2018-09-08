import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
import pytest
from reactors.utils import Reactor


def test_linked_reactors_present():
    '''Ensure critical properties are present and the right class'''
    r = Reactor()
    assert 'linked_reactors' in r.settings.keys()

def test_resolve_valid_actor_id():
    '''If passed an actorID, return it'''
    valid_actor_id = 'OZYYyRpreyYBz'
    invalid_actor_id = 'rRpyeOZYYyYBz'
    r = Reactor()
    id = r.resolve_identifier(valid_actor_id)
    assert id == valid_actor_id
    id = r.resolve_identifier(invalid_actor_id)
    assert id == invalid_actor_id


def test_resolve_app_id():
    '''If passed an Agave appID, return it'''
    private_app_id = 'chimichangas-2.0.0'
    public_app_id = 'chimichangas-2.0.0u1'
    invalid_app_id = 'chimichangas'
    r = Reactor()
    id = r.resolve_identifier(private_app_id)
    assert id == private_app_id
    id = r.resolve_identifier(public_app_id)
    assert id == public_app_id
    id = r.resolve_identifier(invalid_app_id)
    assert id == invalid_app_id


def test_linked_reactors_lookup():
    '''If passed an alias declared in config.yml, return it'''
    valid_alias = 'taconator'
    invalid_alias = 'burritonator'
    r = Reactor()
    id = r.resolve_identifier(valid_alias)
    assert id == 'wZbBo78V1JPZQ'
    id = r.resolve_identifier(invalid_alias)
    # resolve_identifier returns its input if no resolution is possible
    assert id == invalid_alias
