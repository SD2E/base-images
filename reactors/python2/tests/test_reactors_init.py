import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/tacconfig')
import pytest
from reactors.utils import Reactor


def test_init():
    os.environ['_REACTOR_REDACT'] = 'Very Secret Password'
    r = Reactor()
    r.logger.debug(r.settings)
