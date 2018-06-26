import os
import sys
from builtins import int
from past.builtins import basestring

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
import pytest
from requests.exceptions import HTTPError
from reactors.runtime import Reactor
from reactors import agaveutils


# @pytest.mark.parametrize("system,path,fail", [
#     ('data-sd2e-community', '/abcdef', True),
#     ('data-sd2e-community', '/sample', False)
# ])
# def test_mkdir(system, path, fail):
#     r = Reactor()

#     if fail is False:
#         made_dir = agave_mkdir(r.client, 'unit_test', system, path)
#         assert made_dir is True
#     else:
#         with pytest.raises(Exception):
#             made_dir = agave_mkdir(r.client, 'unit_test', system, path)


@pytest.mark.parametrize("system,path,file,fail", [
    ('data-sd2e-community', '/sample/tacc-cloud/ZZZ.png', 'ZZZ.png', True),
    ('data-sd2e-community', '/sample/tacc-cloud/672.png', '672.png', False)
])
def test_files_get(system, path, file, fail):
    r = Reactor()
    if fail is False:
        f = agaveutils.files.get(r.client, path, system, file, retries=3)
        assert os.path.basename(f) == file
    else:
        with pytest.raises(Exception):
            agaveutils.files.get(r.client, path, system, file, retries=2)
