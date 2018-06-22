import os
import sys
from builtins import int
from past.builtins import basestring

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT)
sys.path.append('/reactors')
import pytest
from reactors.utils import process


def test_process_run(caplog, capsys, monkeypatch):
    '''Ensure various properties are present and the right class'''
    cmd_list = ['env']
    result = process.run(cmd_list)
    assert 'cmdline' in result
    assert 'return_code' in result
    assert 'elapsed_msec' in result
    assert 'output' in result

    assert isinstance(result.return_code, int)
    assert isinstance(result.elapsed_msec, (int, float))
    assert isinstance(result.cmdline, (basestring))
    assert isinstance(result.output, (basestring))
    # PATH is going to be in all ENVs
    assert 'PATH' in result.output
    assert result.return_code == 0


@pytest.mark.parametrize("command,permissive,fails", [
    ("xzxzxzxz", False, True),
    ("xzxzxzxz", True, False),
    ("env", False, False),
    ("env", True, False)
])
def test_process_run_exceptions(command, permissive, fails):
    """Test that exceptions are raised where expected"""
    if not isinstance(command, list):
        cmd = [command]
    else:
        cmd = command

    try:
        if fails:
            with pytest.raises(Exception):
                process.run(cmd, permissive=permissive)
        else:
            process.run(cmd, permissive=permissive)
    except Exception:
        pass


def test_process_run_warn_timeout(caplog, capsys):
    cmd_list = ['env']
    process.run(cmd_list, timeout=300)
    assert 'not implemented' not in caplog.text
