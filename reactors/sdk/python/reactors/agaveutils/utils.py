"""
Helper functions for working with Agave and Reactors APIs

```python
from agaveutils import *
```
"""
from __future__ import print_function

import re
import os
import time
from agavepy.agave import Agave
from attrdict import AttrDict


MAX_ELAPSED = 300
MAX_RETRIES = 5
FILES_HTTP_LINK_TYPES = ('media', 'download')
FILES_COMPATIBLE_APIS = ('files', 'jobs')
PWD = os.getcwd()

# TODO: Support nonces
# TODO: Support sending URL parameters
# TODO: Support binary FIFO?

# Normally, one can just inspect her API client to get these values
# but because Abaco creates ephemeral API clients using impersonation
# it's not always perfectly possible. These functions consult the
# local Abaco runtime context before trying heroically to pull the
# values out of the API client itself. This should preserve our ability
# to debug locally while still being able to access these three essential
# values from within Abaco functions.


def get_api_server(ag):
    '''Get current API server URI'''
    if os.environ.get('_abaco_api_server'):
        return os.environ.get('_abaco_api_server')
    elif ag.token is not None:
        try:
            return ag.token.api_server
        except Exception as e:
            print("ag.token was None: {}".format(e))
            pass
        return None
    else:
        print("Used hard-coded value for API server")
        return None


def get_api_token(ag):
    '''Get API access_token'''
    if os.environ.get('_abaco_access_token'):
        return os.environ.get('_abaco_access_token')
    elif ag.token is not None:
        try:
            return ag.token.token_info.get('access_token')
        except Exception as e:
            print("ag.token was None: {}".format(e))
            pass
        return None
    else:
        print("Failed to retriev API access_token")
        return ""


def get_api_username(ag):
    '''Get current API username'''
    if os.environ.get('_abaco_username'):
        return os.environ.get('_abaco_username')
    elif ag is not None:
        try:
            return ag.username
        except Exception as e:
            print("ag was None: {}".format(e))
        return None
    else:
        print("No username could be determined")
        return None
