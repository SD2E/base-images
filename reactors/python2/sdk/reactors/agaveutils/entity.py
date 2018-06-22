"""
Functions for working with Agave namespace entities
"""
import re

# Derived from agave-flat/agave-apps/apps-core/src/main/java/org/iplantc/service/apps/model/Software.java
APPID_REGEX = '(^[a-zA-Z0-9_\\-\\.]+)\\-((?:0|[1-9]+[\\d]*)[\\.\\d]+)(u[0-9]+)?$'
APPID_MAX_LENGTH = 64


def is_appid(textString, useApi=False, agaveClient=None):
    """
    Validate whether textString is an Agave appId

    Positional parameters:
    textString: str - the candidate text string

    Not implemented:
    useApi: bool - try looking the Id up via apps.get
    agaveClient: Agave client - required for useApi
    """
    if len(textString) > APPID_MAX_LENGTH:
        return False

    if re.match(APPID_REGEX, textString):
        return True
    else:
        return False
