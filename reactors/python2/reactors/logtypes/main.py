'''
Set up a logger with optional support for a logfile and STDERR reporting

Usage: logger = get_logger(name, log_level, log_file)
'''
from __future__ import unicode_literals

import json
import os
import time
import logging

from .slack import SlackHandler
from .logstash import LogstashPlaintextHandler

# don't redact strings less than this size
MIN_REDACT_LEN = 4
# possible log levels
LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')
# default log file to be used when using the the combined strategy
LOG_FILE = None
# default log level
LOG_LEVEL = 'DEBUG'

# log strategies that can be used. with combined, all logs go to one file;
# with split, each pikaview has its own log file.
LOG_FILE_STRATEGIES = ('split', 'combined')

# default log strategy
LOG_FILE_STRATEGY_DEFAULT = 'combined'

# Working directory - home of logs
PWD = os.getcwd()


def get_log_file_strategy():
    return LOG_FILE_STRATEGY_DEFAULT


def get_log_file(name):
    return LOG_FILE


class RedactingFormatter(object):
    """Specialized formatter used to sanitize log messages"""
    def __init__(self, orig_formatter, patterns):
        self.orig_formatter = orig_formatter
        self._patterns = patterns

    def format(self, record):
        msg = self.orig_formatter.format(record)
        for pattern in self._patterns:
            if len(pattern) > MIN_REDACT_LEN:
                msg = msg.replace(pattern, "*****")
        return msg

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)


def _get_logger(name, subname, log_level):

    logger_name = '.'.join([name, subname])
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    return logger


def _get_formatter(name, subname, redactions, timestamp):

    if timestamp is False:
        LOG_FORMAT = "{} %(levelname)s %(message)s".format(name)
    else:
        LOG_FORMAT = "{} %(asctime)s %(levelname)s %(message)s".format(name)

    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
    logging.Formatter.converter = time.gmtime
    f = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATEFORMAT)
    f.converter = time.gmtime
    f = RedactingFormatter(f, patterns=redactions)
    return f


def _get_logstash_formatter(name, subname, redactions, fields, timestamp):

    logstruct = {'timestamp': '%(asctime)s',
                 'message': '%(message)s',
                 'level': '%(levelname)s'}
    for (k, v) in list(fields.items()):
        logstruct[k] = v

    JSON_FORMAT = json.dumps(logstruct, indent=None, separators=(',', ':'))
    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"

    f = logging.Formatter(fmt=JSON_FORMAT, datefmt=DATEFORMAT)
    f.converter = time.gmtime
    f = RedactingFormatter(f, patterns=redactions)
    return f


def get_screen_logger(name,
                      subname=None,
                      settings={},
                      redactions=[],
                      fields={},
                      timestamp=False):

    log_level = settings.get('logs', {}).get('level', LOG_LEVEL)
    logger = _get_logger(name=name, subname=subname,
                         log_level=log_level)

    # Create the STDERR logger
    text_formatter = _get_formatter(name, subname, redactions, timestamp)
    stderrHandler = logging.StreamHandler()
    stderrHandler.setFormatter(text_formatter)
    logger.addHandler(stderrHandler)

    # Create FILE logger (mirror)
    log_file = settings.get('logs', {}).get('file', None)
    if log_file is not None:
        log_file_path = os.path.join(PWD, log_file)
        fileHandler = logging.FileHandler(log_file_path)
        fileHandler.setFormatter(text_formatter)
        logger.addHandler(fileHandler)

    # Create NETWORK logger if log_token present
    log_token = settings.get('logs', {}).get('token', None)
    config = settings.get('logger', None)
    if log_token is not None and config is not None:
        json_formatter = _get_logstash_formatter(name, subname,
                                                 redactions,
                                                 fields,
                                                 timestamp)

        networkHandler = LogstashPlaintextHandler(config, log_token)
        networkHandler.setFormatter(json_formatter)
        logger.addHandler(networkHandler)

    # TODO: Forward to log aggregator if token is set
    return logger


# def get_stream_logger(name, subname, config, token,
#                       log_level=LOG_LEVEL,
#                       redactions=[],
#                       timestamp=False,
#                       fields={}):
#     logger = _get_logger(name=name, subname=subname, log_level=LOG_LEVEL,
#                          redactions=redactions)
#     formatter = _get_logstash_formatter(name, subname,
#                                         redactions, fields, timestamp)

#     streamLogger = LogstashPlaintextHandler(config, token)
#     streamLogger.setFormatter(formatter)
#     logger.addHandler(streamLogger)
#     return logger


def get_slack_logger(name, subname,
                     settings={},
                     redactions=[],
                     timestamp=False):

    '''Returns a logger object that can post to Slack'''
    log_level = settings.get('logs', {}).get('level', LOG_LEVEL)
    logger = _get_logger(name=name, subname=subname, log_level=log_level)
    text_formatter = _get_formatter(name, subname, redactions, timestamp)
    slacksettings = settings.get('slack', {})
    slackHandler = SlackHandler(slacksettings)
    slackHandler.setFormatter(text_formatter)
    logger.addHandler(slackHandler)
    return logger


def get_logger(name, subname=None, log_level=LOG_LEVEL, log_file=None,
               redactions=[], timestamp=False):
    '''Legacy alias to get_stderr_logger'''
    return get_screen_logger(name, subname, log_level, redactions)

# Verified Py3 compatible
