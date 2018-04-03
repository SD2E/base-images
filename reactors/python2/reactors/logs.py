'''
Set up a logger with optional support for a logfile and STDERR reporting

Usage: logger = get_logger(name, log_level, log_file)
'''

import os
import time
import logging

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


def get_logger(name, subname, log_level=LOG_LEVEL, log_file=LOG_FILE):
    """
    Returns a properly configured STDERR logger
         name (str) should be the module name.
    """
    FORMAT = "%(asctime)s [%(levelname)s] {}:{} - %(message)s".format(name, subname)
    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
    logging.Formatter.converter = time.gmtime

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if log_file is not None:
        log_file_path = os.path.join(PWD, log_file)
        handler = logging.FileHandler(log_file_path)
        handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFORMAT))
        handler.setLevel(log_level)
        logger.addHandler(handler)

    stderrLogger = logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFORMAT))
    logger.addHandler(stderrLogger)

    return logger

# Verified Py3 compatible
