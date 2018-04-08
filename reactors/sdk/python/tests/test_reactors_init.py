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
    assert r.username is not None
    assert isinstance(r.local, bool)
    assert isinstance(r.context, AttrDict)
    assert isinstance(r.state, dict)
    assert isinstance(r.client, Agave)
    assert isinstance(r.logger, Logger)


# def test_localonly(monkeypatch):
#     '''Check LOCALONLY x Reactor.local behavior'''
#     monkeypatch.setenv('LOCALONLY', 1)
#     r = Reactor()
#     rlocal = r.local
#     assert rlocal is True
    # monkeypatch.setenv('LOCALONLY', 0)
    # p = Reactor()
    # plocal = p.local
    # assert plocal is False
