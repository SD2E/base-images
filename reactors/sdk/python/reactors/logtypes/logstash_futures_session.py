import json
import requests
import logging
import logging.handlers
import traceback
from requests_futures.sessions import FuturesSession

# Adapted from https://github.com/loggly/loggly-python-handler/blob/master/loggly/handlers.py

session = FuturesSession()


def bg_cb(sess, resp):
    """Noop the response so logging is fire-and-forget"""
    pass

# As per https://github.com/ross/requests-futures#working-in-the-background


def response_hook_noop(resp, *args, **kwargs):
    """Noop the response so logging is fire-and-forget
    """
    pass


class LogstashPlaintextHandler(logging.Handler):
    """Py2-3.4 compatible method to send logs to LogStash HTTP handler"""

    def __init__(self, config, client_secret):
        # print("LogstashPlaintextHandler.futures_session")
        if not isinstance(config, dict):
            config = {}
        self.uri = config.get('uri', 'http://127.0.0.1') +\
            config.get('path', '/logger')
        self.client_key = config.get('client_key', 'xDEADBEEF')
        self.token = client_secret
        super(LogstashPlaintextHandler, self).__init__()

    def get_full_message(self, record):
        if record.exc_info:
            return '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            return record.getMessage()

    def emit(self, record):

        post_uri = self.uri
        uname = self.client_key
        passwd = self.token
        fmted = self.format(record)

        try:
            log_entry = json.loads(fmted)
        except Exception:
            log_entry = fmted

        headers = {'Content-type': 'application/json'}

        if post_uri is not None and passwd is not None:
            try:
                # As per https://github.com/ross/requests-futures#working-in-the-background
                session.post(post_uri, auth=(uname, passwd), json=log_entry,
                             headers=headers,
                             hooks={'response': response_hook_noop})
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)
        else:
            pass
