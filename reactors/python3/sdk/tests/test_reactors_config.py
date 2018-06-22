import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
import pytest
from reactors.utils import Reactor


def test_read_default():
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    assert 'logs' in r.settings.keys()


def test_read_override(monkeypatch):
    '''Ensure various properties are present and the right class'''
    r = Reactor()
    assert 'logs' in r.settings.keys()
    assert r.settings.logs.level == 'DEBUG'
    monkeypatch.setenv('_REACTOR_LOGS_LEVEL', 'INFO')
    p = Reactor()
    assert p.settings.logs.level == 'INFO'
