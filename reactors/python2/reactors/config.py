"""
Read in configuration from config.yml into an AttrDict
Search path: Root directory, working directory,
             config.py install directory
Optional: Override any 1st or 2nd level key
          by setting an ENV variable named
          _REACTOR_KEY1 or _REACTOR_KEY1_KEY2
"""

# Usage: from config import settings
import os
import logging
import yaml
from attrdict import AttrDict

HERE = os.path.dirname(os.path.abspath(__file__))
PWD = os.getcwd()
ROOT = '/'
CONFIG = 'config.yml'
NAMESPACE = '_REACTOR_'


def read_config():
    """
    Reads CONFIG into 'settings', allowing optional
    ENV-based overrides via namespaced variables
    """
    config = AttrDict()
    # File-based configuration.
    places = [ROOT, PWD, HERE]
    for p in places:
        fname = os.path.join(p, CONFIG)
        if os.path.isfile(fname):
            try:
                with open(fname, "r") as conf:
                    try:
                        config = yaml.safe_load(conf)
                        if config is None:
                            config = {}
                        config = AttrDict(conf)
                    except yaml.YAMLError as e:
                        if hasattr(e, 'problem_mark'):
                            mark = e.problem_mark
                            print(
                                "YAML error in {}: Line {} / Col {}".format(
                                    fname, mark.line + 1, mark.column + 1))
                        else:
                            print("YAML error in {}: {}".format(fname, e))
                break
            except Exception as e:
                logging.exception(e)
                pass

    # TODO - Check for duplicate keys coming in from ENV
    # TODO - Check that get/set from ENV is successful
    for level1 in config.keys():
        if (config[level1] is None) or (type(config[level1])) is str:
            env_var = NAMESPACE + level1
            env_var = env_var.upper()
            if os.environ.get(env_var):
                config[level1] = os.environ.get(env_var)
        elif type(config[level1]) is dict:
            for level2 in config[level1].keys():
                if (config[level1][level2] is None) or (type(config[level1][level2])) is str:
                    env_var = NAMESPACE + level1 + '_' + level2
                    env_var = env_var.upper()
                    if os.environ.get(env_var):
                        config[level1][level2] = os.environ.get(env_var)
        else:
            pass

    return config


settings = read_config()
