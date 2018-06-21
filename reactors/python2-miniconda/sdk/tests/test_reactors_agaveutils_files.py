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
from reactors.agaveutils.files import *


@pytest.mark.parametrize("system,path,fail", [
    ('data-sd2e-community', '/abcdef', True),
    ('data-sd2e-community', '/sample', False)
])
def test_mkdir(system, path, fail):
    r = Reactor()

    if fail is False:
        made_dir = agave_mkdir(r.client, 'unit_test', system, path)
        assert made_dir is True
    else:
        with pytest.raises(Exception):
            made_dir = agave_mkdir(r.client, 'unit_test', system, path)

