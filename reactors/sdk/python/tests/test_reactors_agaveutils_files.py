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

PASS_RETRIES = 5
FAIL_RETRIES = 2


@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Too time intensive")
@pytest.mark.parametrize("system,basepath,willpass", [
    ('data-sd2e-community', '/sample/taco-cloud', False),
    ('data-sd2e-community', '/sample/tacc-cloud', True)
])
def test_files_mkdir(system, basepath, willpass):
    r = Reactor()

    if willpass is True:
        made_dir = agaveutils.files.mkdir(r.client,
                                          'unit_test',
                                          system,
                                          basepath,
                                          retries=PASS_RETRIES)
        assert made_dir is True
    else:
        with pytest.raises(Exception):
            made_dir = agaveutils.files.mkdir(r.client,
                                              'unit_test',
                                              system,
                                              basepath,
                                              retries=FAIL_RETRIES)


@pytest.mark.skipif(sys.version_info.major >= 3,
                    reason="Too time intensive")
@pytest.mark.parametrize("system,path,file,willpass", [
    ('data-sd2e-community', '/sample/tacc-cloud/ZZZ.png', 'ZZZ.png', False),
    ('data-sd2e-community', '/sample/tacc-cloud/672.png', '672.png', True)
])
def test_files_get(system, path, file, willpass):
    r = Reactor()
    if willpass is True:
        f = agaveutils.files.get(r.client, path,
                                 system, file, retries=PASS_RETRIES)
        assert os.path.basename(f) == file
    else:
        with pytest.raises(Exception):
            agaveutils.files.get(r.client, path,
                                 system, file, retries=FAIL_RETRIES)
    try:
        os.unlink(file)
    except Exception:
        pass
