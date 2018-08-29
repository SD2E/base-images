import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
import pytest
from reactors.utils import Reactor
import testdata


@pytest.fixture(scope='session')
def test_data():
    return testdata.AbacoJSONmessages().data()


def test_validate_schema():
    '''Ensure at least one schema can validate'''
    pytest.skip()
    r = Reactor()
    messagedict = json.loads('{"key": "value"}')
    valid = r.validate_message(messagedict,
                               messageschema='/message.jsonschema',
                               permissive=False)
    assert valid is True


def test_abacoschemas(test_data):
    '''Test all known Abaco schemas'''
    pytest.skip()
    r = Reactor()
    exceptions = []
    for comp in test_data:
        mdict = comp.get('object', {})
        schem = os.path.join('/abacoschemas', comp.get('schema'))
        # perm = True
        validates = comp.get('validates')
        try:
            r.validate_message(mdict,
                               messageschema=schem,
                               permissive=False)
        except Exception as e:
            # The message did not validate tho we expected it to
            if validates is True:
                exceptions.append(e)

    if len(exceptions) > 0:
        raise Exception("Exceptions: {}".format(exceptions))
