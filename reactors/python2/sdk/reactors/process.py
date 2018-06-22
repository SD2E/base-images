"""Run subprocesses from within Python"""
import subprocess
from datetime import datetime
from attrdict import AttrDict
import warnings

DEFAULT_TIMEOUT = 60  # 1 minute


def run(command_list=[], permissive=False, shell=False, timeout=None):
    """
    Run a child or subshell process.

    Parameters:
    exec_params - list - Parameters in exec form
    permissive  - bool - Ignore errors
    shell       - bool - Execute command by way of a shell

    Usage:
      # List system logs directory
      params=['ls', '-alth', '/var/log']
      process.run(params)

    Returns an AttrDict of response attributes.

    """

    # timeout remains unimplemented pending Py3-nativity
    if timeout is not None:
        warnings.warn('timeout parameter for run is not implemented')

    response = AttrDict(
        {'cmdline': None,
         'return_code': None,
         'output': None,
         'elapsed_msec': None})

    t1 = datetime.now()
    try:
        response.cmdline = subprocess.list2cmdline(command_list)
        out_bytes = subprocess.check_output(
            command_list, shell=shell, stderr=subprocess.STDOUT)
        response.output = out_bytes.decode()
        response.return_code = 0
        t2 = datetime.now()
        delta = t2 - t1
        response.elapsed_msec = int(delta.total_seconds() * 1000)
    except subprocess.CalledProcessError as e:
        if permissive is True:
            response.output = e.output
            response.return_code = e.returncode
        else:
            raise OSError(e)

    return response
