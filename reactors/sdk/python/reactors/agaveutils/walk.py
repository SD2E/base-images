'''Demonstratively recursive permission grants using AgavePy'''

import hashlib
import os
import sys
import logging
from time import time, gmtime
from agavepy.agave import Agave

FILES = True

COMPLETED_TEMP = []
MAX_COMPLETED_TEMP = 25
COMPLETED = []

RESTART_FILE = '.agaveutils.walk.restart'
EXCLUDES_FILE = '.agaveutils.walk.excludes'
PWD = os.getcwd()

FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)

def tree(ag, system, path, uname='world', pem='READ', rec=False):
    '''Main function. Minimalist directory tree crawler'''

    dirs, files = listdir(ag, system, path)[:2]
    logger.info(path)
    walk(path, dirs, files, ag, system, uname, pem, rec)
    return True


def walk(root, dirs, files, ag, system, uname, pem='READ', rec=False):
    if FILES and files:
        for name in files:
            fpath = os.path.join(root, name)
            logger.debug(fpath)
            updatepem(ag, system, fpath, uname, pem, rec)
    for pos, neg, name in enumerate2(dirs):
        dpath = os.path.join(root, name)
        logger.info(dpath)
        updatepem(ag, system, dpath, uname, pem, rec)
        try:
            dirs, files = listdir(ag, system, dpath)[:2]
        except Exception:
            pass
        else:
            walk(dpath, dirs, files, ag, system, uname, pem, rec)


def listdir(ag, system, fpath):
    dirs, files, links = [], [], []
    for file_obj in ag.files.list(systemId=system, filePath=fpath):
        if file_obj['format'] == 'folder':
            if file_obj['name'] != '.':
                dirs.append(file_obj['name'])
        elif file_obj['format'] in ('raw', 'file'):
            files.append(file_obj['name'])
    return dirs, files, links


def _listdir(path):
    dirs, files, links = [], [], []
    for name in os.listdir(path):
        path_name = os.path.join(path, name)
        if os.path.isdir(path_name):
            dirs.append(name)
        elif os.path.isfile(path_name):
            files.append(name)
        elif os.path.islink(path_name):
            links.append(name)
    return dirs, files, links


def enumerate2(sequence):
    length = len(sequence)
    for count, value in enumerate(sequence):
        yield count, count - length, value


def updatepem(ag, system, fpath, uname, pem, rec=False):
    '''Send an pems update request'''
    global COMPLETED_TEMP

    try:
        hashed_pem = hash_pem(system, fpath, uname, pem)
        if hashed_pem not in COMPLETED:
            ag.files.updatePermissions(systemId=system,
                                       filePath=fpath,
                                       body={'username': uname,
                                             'permission': pem,
                                             'recursive': rec})
            COMPLETED_TEMP.append(hashed_pem)
            update_completed()
        else:
            logger.debug("{}/{} skipped".format(system, fpath))
    except Exception as e:
        raise Exception(
            "Error ({}) setting permission {}:{} on {}/{}".format(
                e, uname, pem, sys, fpath))
        return False

    return True


def update_completed(force=False):
    '''Update the COMPLETED list and persist if needed'''
    # don't amend every time - we just need an approximate
    # marking in the list of file paths to avoid loads of
    # redundant pems calls
    global COMPLETED
    global COMPLETED_TEMP
    global MAX_COMPLETED_TEMP

    if (len(COMPLETED_TEMP) >= MAX_COMPLETED_TEMP) or force is True:
        if amend_restart_file():
            COMPLETED.extend(COMPLETED_TEMP)
            COMPLETED_TEMP = []
            return True
        else:
            return False
        # apppend _COMPLETED_TEMP to to file
        # empty COMPLETED_TEMP
        return False


def get_restart_filename(system, fpath):
    '''Return uniquely-named state file for system/path'''
    temp_path = '/'.join([system, fpath])
    fname_root = hashlib.md5(temp_path).hexdigest()
    return '.' + fname_root + '.restart'


def hash_pem(system, fpath, uname, pem):
    '''Return a hash representing a pems action'''
    temp_path = '.'.join([system, fpath, uname, pem])
    return hashlib.md5(temp_path).hexdigest()


def load_excludes_file(file_name):
    '''Load in a list of regexes that exclude path names'''
    return True


def load_restart_file(file_name):
    '''Populate the COMPLETED list from a local file'''
    global COMPLETED
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r+') as f:
                COMPLETED = f.readlines()
            COMPLETED = [x.strip() for x in COMPLETED]
            logger.info("Restart file {} contained {} entries".format(
                file_name, len(COMPLETED)))
        except Exception as e:
            logger.debug(
                "Restart file {} was not accessible".format(file_name))
            pass

    return True


def amend_restart_file():
    '''Append a batch of completed pem hashes to disk'''
    global RESTART_FILE
    try:
        with open(RESTART_FILE, 'a+') as f:
            for pem_hash in COMPLETED_TEMP:
                f.write(pem_hash + '\n')
        f.close()
        return True
    except Exception as e:
        logger.warning("Unable to write to {}: {}".format(RESTART_FILE, e))
        return False


def main():

    global RESTART_FILE

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFORMAT))
    logger.addHandler(handler)

    ts1 = time()
    ag = Agave.restore()
    system_id = sys.argv[1]
    fpath = sys.argv[2]

    RESTART_FILE = get_restart_filename(system_id, fpath)

    load_restart_file(RESTART_FILE)
    tree(ag, system_id, fpath)
    # flush
    update_completed(force=True)
    elapsed = time() - ts1
    logger.info("Elapsed: {} sec".format(elapsed))


if __name__ == '__main__':
    main()
