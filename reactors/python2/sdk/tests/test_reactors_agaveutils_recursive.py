import os
import sys
from builtins import int
from past.builtins import basestring

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
import pytest
from reactors.utils import Reactor
from reactors.agaveutils.recursive import PemAgent, __version__


def test_init_pemagent():
    r = Reactor()
    assert isinstance(r.pemagent, PemAgent)
    assert r.pemagent.version == __version__


@pytest.mark.parametrize("system,path,fail", [
    ('data-sd2e-community', '/abcdef', True),
    ('data-sd2e-community', '/sample', False)
])
def test_pemagent_listdir(system, path, fail):
    r = Reactor()
    if fail is False:
        assert isinstance(r.pemagent.listdir(system, path), tuple)
    else:
        with pytest.raises(Exception):
            r.pemagent.listdir(system, path)
