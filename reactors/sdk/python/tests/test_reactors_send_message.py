from reactors.utils import Reactor
from agavepy.agave import AgaveError
import pytest
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')


@pytest.mark.parametrize("actor_id, message, success", [
    ('gO0JeWaBM4p3J', {'text': 'gO0JeWaBM4p3J'}, True),
    ('sd2eadm-listener', {'text': 'sd2eadm-listener'}, True),
    ('meep-meep-meep', {'text': 'meep-meep-meep'}, False)])
def test_reactors_send_message(actor_id, message, success):
    r = Reactor()
    if success is True:
        exec_id = r.send_message(actor_id, message, retryMaxAttempts=1, ignoreErrors=False)
        assert exec_id is not None
    else:
        with pytest.raises(AgaveError):
            r.send_message(actor_id, message, retryMaxAttempts=1, ignoreErrors=False)
