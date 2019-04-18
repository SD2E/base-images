from reactors.utils import Reactor
import pytest
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')


def test_linked_reactors_present():
    '''Ensure critical properties are present and the right class'''
    r = Reactor()
    assert 'linked_reactors' in r.settings.keys()


@pytest.mark.parametrize("self_alias", [('me'), ('self')])
def test_resolve_valid_actor_id_me(self_alias):
    '''If passed an self-alias, return it'''

    r = Reactor()
    assert r.resolve_actor_alias(self_alias) == r.uid


def test_resolve_valid_actor_id():
    '''If passed an actorID, return it'''
    valid_actor_id = 'OZYYyRpreyYBz'
    invalid_actor_id = 'rRpyeOZYYyYBz'
    r = Reactor()
    id = r.resolve_actor_alias(valid_actor_id)
    assert id == valid_actor_id
    id = r.resolve_actor_alias(invalid_actor_id)
    assert id == invalid_actor_id


@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Deprecated functionality")
def test_resolve_app_id():
    '''If passed an Agave appID, return it'''
    private_app_id = 'chimichangas-2.0.0'
    public_app_id = 'chimichangas-2.0.0u1'
    invalid_app_id = 'chimichangas'
    r = Reactor()
    id = r.resolve_actor_alias(private_app_id)
    assert id == private_app_id
    id = r.resolve_actor_alias(public_app_id)
    assert id == public_app_id
    id = r.resolve_actor_alias(invalid_app_id)
    assert id == invalid_app_id
