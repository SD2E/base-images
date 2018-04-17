"""
Helper functions for common filesystem operations with Agave
"""
import re
import os
import time
from agavepy.agave import Agave


PWD = os.getcwd()
MAX_ELAPSED = 300
MAX_RETRIES = 5


def agave_mkdir(agaveClient, dirName, systemId, basePath='/',
                sync=False, timeOut=MAX_ELAPSED):
    """
    Creates a directory dirName on a storage system at basePath

    Like mkdir -p this is imdepotent. It will create the child path
    tree so long as paths are specified correctly, but will do
    nothing if all directories are already in place.
    """
    try:
        agaveClient.files.manage(systemId=systemId,
                                 body={'action': 'mkdir', 'path': dirName},
                                 filePath=basePath)
    except Exception as e:
        raise Exception(
            "Unable to mkdir {} at {}/{}: {}".format(
                dirName, systemId, basePath, e))

    return True


def agave_download_file(agaveClient,
                        agaveAbsolutePath,
                        systemId,
                        localFilename='downloaded',
                        sync=True,
                        timeOut=300):
    """
    Download an Agave-hosted file to cwd()

    Currently, always a synchronous task.
    """
    downloadFileName = os.path.join(PWD, localFilename)
    with open(downloadFileName, 'wb') as f:
        try:
            rsp = agaveClient.files.download(systemId=systemId,
                                             filePath=agaveAbsolutePath)
        except Exception as e:
            raise Exception(
                "Catastrophic error in agave_download_file: {}".format(e))
        if type(rsp) == dict:
            raise Exception(
                "Unable to download {}".format(agaveAbsolutePath))
        for block in rsp.iter_content(2048):
            if not block:
                break
            f.write(block)
    return downloadFileName


def agave_upload_file(agaveClient,
                      agaveDestPath,
                      systemId,
                      uploadFile,
                      sync=True,
                      timeOut=MAX_ELAPSED):
    """
    Upload a file to Agave-managed remote storage.

    If sync is True, the function will wait for the upload to
    complete before returning. Raises exceptions on importData
    or timeout errors.
    """
    try:
        agaveClient.files.importData(systemId=systemId,
                                     filePath=agaveDestPath,
                                     fileToUpload=open(uploadFile))
    except Exception as e:
        raise Exception("Error uploading {}: {}".format(uploadFile, e))

    uploaded_filename = os.path.basename(uploadFile)
    if sync:
        fullAgaveDestPath = os.path.join(agaveDestPath, uploaded_filename)
        wait_for_file_status(
            agaveClient, fullAgaveDestPath, systemId, timeOut)

    return True


def wait_for_file_status(agaveClient, agaveWatchPath,
                         systemId, maxTime=MAX_ELAPSED):
    """
    Synchronously wait for a file's status to reach a terminal state.

    Returns an exception and the final state if it timeout is exceeded. Uses
    exponential backoff to avoid overloading the files server with poll
    requests. Returns True on success.
    """

    # Note: This is not reliable if a lot of actions are taken on the
    #       file, such as serially re-uploading it, granting pems, etc
    #       because history is not searchable nor does it distinguish
    #       between terminal physical states (done uploading) and
    #       emphemeral actions (pems grants, downloads, etc). A reliable
    #       implementation might spawn a temporary callback channel
    #       (i.e. requestbin) subscribed to only terminal events, then
    #       monitor its messages to watch for completion.
    TERMINAL_STATES = ['STAGING_COMPLETED', 'TRANSFORMING_COMPLETED',
                       'CREATED', 'DOWNLOAD']

    assert maxTime > 0
    assert maxTime <= 1000

    delay = 0.150  # 300 msec
    expires = (time.time() + maxTime)
    stat = None
    ts = time.time()

    while (time.time() < expires):
        elapsed = time.time() - ts
        try:
            hist = agaveClient.files.getHistory(systemId=systemId,
                                                filePath=agaveWatchPath)
            stat = hist[-1]['status']
            if stat in TERMINAL_STATES:
                return True
        except Exception as e:
            # we have to swallow this exception because status isn't available
            # until the files service picks up the task. sometimes that's
            # immediate and sometimes it's backlogged - we dont' want to fail
            # just because it takes a few seconds or more before status becomes
            # available since we went through the trouble of setting up
            # exponential backoff!
            pass
        time.sleep(delay)
        delay = (delay * 1.1)

    raise Exception(
        "Status transition for {} exceeded {} sec. Last status: {}".format(
            agaveWatchPath, maxTime, stat))
