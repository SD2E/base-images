'''Recursively apply permission grants using AgavePy'''
import os
import sys
import logging
from time import sleep
from random import random

__version__ = '0.1.0'

FILES = True
FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"


class PemAgent(object):
    """Specialized Agave class for doing recursive pem management"""
    def __init__(self, agaveClient, loglevel='INFO'):
        """
        Initialize a PemAgent object

        Positional parameters:
        agaveClient - an initialaized Agave object

        Keyword parameters:
        loglevel - Set the logging level. DEBUG is good for diagnosing issues.

        Returns:
        - PemAgent
        """
        self.client = agaveClient
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        stderrLogger = logging.StreamHandler()
        stderrLogger.setFormatter(
            logging.Formatter(FORMAT, datefmt=DATEFORMAT))
        self.logger.addHandler(stderrLogger)
        self.version = __version__

    def grant(self, system, abspath, username='world',
              pem='READ', recursive=False, permissive=True):
        '''Recursively crawl abspath and grant pem'''
        self.updatepem(system, abspath, username, pem, recursive)
        dirs, files = self.listdir(system, abspath)[:2]
        self.logger.debug("grant {} to {} on path agave://{}{}".format(
            pem, username, system, abspath))
        try:
            self.walk(abspath, dirs, files, system, username, pem, recursive)
        except Exception as e:
            if permissive is True:
                self.logger.error(
                    "grant failed on agave://{}{} (error: {})".format(
                        system, abspath, e))
                return False
            else:
                raise Exception(e)
                return False

        return True

    def walk(self, root, dirs, files, system, username, pem='READ', rec=False):

        if FILES and files:
            for name in files:
                fpath = os.path.join(root, name)
                self.updatepem(system, fpath, username, pem, rec)
        for pos, neg, name in self.enumerate2(dirs):
            dpath = os.path.join(root, name)
            self.updatepem(system, dpath, username, pem, rec)
            try:
                dirs, files = self.listdir(system, dpath)[:2]
            except Exception:
                pass
            else:
                self.walk(dpath, dirs, files, system, username, pem, rec)

    def updatepem(self, system, fpath, username, pem,
                  rec=False, permissive=True):
        '''Send an pems update request'''

        try:
            self.client.files.updatePermissions(systemId=system,
                                                filePath=fpath,
                                                body={'username': username,
                                                      'permission': pem,
                                                      'recursive': rec})
            # introduce pseudo-random delay between pems calls
            sleep(0.5 * random())
        except Exception as e:
            if permissive is True:
                self.logger.error(
                    "updatepem failed on agave://{}{} (error: {})".format(
                        sys, fpath, e))
                return False
            else:
                raise Exception(e)
                return False

        return True

    def enumerate2(self, sequence):
        length = len(sequence)
        for count, value in enumerate(sequence):
            yield count, count - length, value

    def listdir(self, system, fpath):
        dirs, files, links = [], [], []
        try:
            for file_obj in self.client.files.list(systemId=system,
                                                   filePath=fpath):
                    if file_obj['format'] == 'folder':
                        if file_obj['name'] != '.':
                            dirs.append(file_obj['name'])
                    elif file_obj['format'] in ('raw', 'file'):
                        files.append(file_obj['name'])
            return dirs, files, links
        except Exception as e:
            raise Exception(e)
