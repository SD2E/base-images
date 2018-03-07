"""Set up one more more logger(s)."""

import time
import logging
from config import settings

# possible log levels
LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')

# default log file to be used when using the the combined strategy
LOG_FILE = 'reactor.log'

# default log level
LEVEL = 'INFO'

# log strategies that can be used. with combined, all logs go to one file;
# with split, each pikaview has its own log file.
LOG_FILE_STRATEGIES = ('split', 'combined')

# default log strategy
LOG_FILE_STRATEGY_DEFAULT = 'combined'


def get_log_file_strategy():
    return LOG_FILE_STRATEGY_DEFAULT


def get_module_log_level(name):
    """Reads config file for a log level set for this module."""
    try:
        log_level = settings.get('logs').get('level')
        if log_level.upper() in LEVELS:
            return log_level
    except AttributeError:
        # if the logs section doesn't exist, use default
        return LEVEL

    if log_level == "":
        return LEVEL


def get_log_file(name):
    return LOG_FILE


def get_logger(name):
    """
    Returns a properly configured STDERR logger
         name (str) should be the module name.
    """
    FORMAT = "[%(levelname)s] %(asctime)s: %(message)s"
    DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"
    logging.Formatter.converter = time.gmtime

    logger = logging.getLogger(name)
    level = get_module_log_level(name)
    logger.setLevel(level)

    # handler = logging.FileHandler(get_log_file(name))
    # handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFORMAT))
    # handler.setLevel(level)
    # logger.addHandler(handler)

    stderrLogger = logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFORMAT))
    logger.addHandler(stderrLogger)

    return logger
