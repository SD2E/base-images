"""
Utility library for supporting container-local,
global POSIX, and eventually, object and document
storage for TACC Reactors
"""

import os
import tempfile
from attrdict import AttrDict

HERE = os.getcwd()
_paffs = AttrDict({'default': HERE,
                   'user': {'work': HERE},
                   'project': {'archive': HERE,
                               'data': HERE},
                   'reactor': {'scratch': os.getcwd(),
                               'temp': tempfile.mkdtemp(prefix='abaco-',
                                                        dir='/tmp')}})


if os.environ.get('_PROJ_CORRAL') is not None:
    if os.path.isdir(os.environ.get('_PROJ_CORRAL')):
        _paffs.project.archive = os.environ.get('_PROJ_CORRAL')

if os.environ.get('_PROJ_STOCKYARD') is not None:
    if os.path.isdir(os.environ.get('_PROJ_STOCKYARD')):
        _paffs.project.data = os.environ.get('_PROJ_STOCKYARD')

if os.environ.get('_USER_WORK') is not None:
    if os.path.isdir(os.environ.get('_USER_WORK')):
        _paffs.user.work = os.environ.get('_USER_WORK')

if os.environ.get('_REACTOR_TEMP') is not None:
    if os.path.isdir(os.environ.get('_REACTOR_TEMP')):
        _paffs.reactor.scratch = os.environ.get('_REACTOR_TEMP')
        _paffs.reactor.default = _paffs.reactor.scratch

paths = _paffs

# Verified Py3 compatible
