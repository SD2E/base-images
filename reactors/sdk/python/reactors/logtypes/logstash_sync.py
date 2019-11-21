import json
import requests
import logging
import logging.handlers
import traceback


class LogstashPlaintextHandler(logging.Handler):
    """Forwards logs on to LogStash HTTP handler"""

    def __init__(self, config, client_secret):
        # print("LogstashPlaintextHandler.sync")

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
                requests.post(post_uri,
                              headers=headers,
                              json=log_entry,
                              auth=(uname, passwd))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                self.handleError(record)
        else:
            pass
