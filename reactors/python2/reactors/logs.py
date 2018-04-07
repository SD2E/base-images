'''
Set up a logger with optional support for a logfile and STDERR reporting

Usage: logger = get_logger(name, log_level, log_file)
'''
from __future__ import unicode_literals

import os
import re
import time
import logging
from builtins import str

# possible log levels
LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')

# default log file to be used when using the the combined strategy
LOG_FILE = None

# default log level
LOG_LEVEL = 'INFO'

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
    def __init__(self, orig_formatter, patterns=[]):
        self.orig_formatter = orig_formatter
        filtered_patterns = []
        for p in patterns:
            # we're not getting into the business of
            # replacing anything but legitimate strings
            if isinstance(p, str):
                filtered_patterns.append(p)
        self._patterns = filtered_patterns

    def format(self, record):
        msg = self.orig_formatter.format(record)
        for pattern in self._patterns:
            msg = msg.replace(pattern, "*****")
        return msg

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)


def get_logger(name, subname=None, log_level=LOG_LEVEL,
               log_file=LOG_FILE, redactions=[]):
    """
    Create an instance of logger

    Positional arguments:
    name - str - the logger name

    Keyword arguments:
    subname - str - logger's secondary name
    log_level - str - the logging level
    log_file - str - filename relative to os.cwd() for logs (optional)
    redact - list - list of strings (no regex!) to filter in log messages
    """
    if subname is None:
        LOG_FORMAT = "%(asctime)s [%(levelname)s] {} - %(message)s".format(name)
    else:
        LOG_FORMAT = "%(asctime)s [%(levelname)s] {}:{} - %(message)s".format(name, subname)

    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
    logging.Formatter.converter = time.gmtime

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    f = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATEFORMAT)
    f.converter = time.gmtime
    f = RedactingFormatter(f, patterns=redactions)

    if log_file is not None:
        log_file_path = os.path.join(PWD, log_file)
        handler = logging.FileHandler(log_file_path)
        handler.setFormatter(f)
        logger.addHandler(handler)

    stderrLogger = logging.StreamHandler()
    stderrLogger.setFormatter(f)
    logger.addHandler(stderrLogger)

    return logger

# Verified Py3 compatible
