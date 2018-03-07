"""
Helper functions for working with Agave and Reactors APIs

```python
from agaveutils import *
```
"""

import re
import os
import time
from agavepy.agave import Agave
from attrdict import AttrDict

MAX_ELAPSED = 300
MAX_RETRIES = 5
FILES_HTTP_LINK_TYPES = ('media', 'download')
FILES_COMPATIBLE_APIS = ('files', 'jobs')
PWD = os.getcwd()

# TODO: Support nonces
# TODO: Support sending URL parameters
# TODO: Support binary FIFO?


def message_reactor(agaveClient, actorId, message,
                    environment={}, ignoreErrors=True,
                    sync=False, senderTags=True,
                    timeOut=MAX_ELAPSED):
    """
    Send a message to an Abaco actor by its ID

    Returns execution ID. If ignoreErrors is True, this is fire-and-forget.
    Otherwise, failures raise an Exception to handled by the caller.
    """

    SPECIAL_VARS = {'_abaco_actor_id': 'x_src_actor_id',
                    '_abaco_execution_id': 'x_src_execution_id',
                    'JOB_ID': 'x_src_job_id',
                    'EVENT': 'x_src_job_event',
                    '_event_uuid': 'x_external_event_id'}
    pass_envs = {}
    if senderTags is True:
        for env in SPECIAL_VARS.keys():
            if os.environ.get(env):
                pass_envs[SPECIAL_VARS[env]] = os.environ.get(env)

    execution = {}
    try:
        execution = agaveClient.actors.sendMessage(actorId=actorId,
                                                   body={'message': message},
                                                   environment=pass_envs)
    except Exception as e:
        errorMessage = "Error messaging actor {}: {}".format(actorId, e)
        if ignoreErrors:
            pass
        else:
            raise Exception(errorMessage)

    try:
        execId = execution.executionId
        return execId
    except Exception as e:
        errorMessage = " Message to {} failed: {}".format(actorId, e)
        if ignoreErrors:
            pass
        else:
            raise Exception(errorMessage)


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
    TERMINAL_STATES = ['CREATED', 'TRANSFORMING_COMPLETED', 'DOWNLOAD']

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


def to_agave_uri(systemId=None, dirPath=None, fileName=None, validate=False):
    """
    Construct an Agave URI for system ID, path, (filename)


    Validation that URI points to a real resource is not implemented.
    Should we choose to do this, it will be expensive since it will
    involve at least one API call.
    """
    if (systemId is not None) and (dirPath is not None):
        uri = 'agave://' + systemId + os.path.join('/', dirPath)
        if fileName is not None:
            uri = os.path.join(uri, fileName)
        return uri
    else:
        raise ValueError('Both systemId and dirPath must be specified')


def from_tacc_s3_uri(uri=None, Validate=False):
    """
    Parse a TACC S3 URI into a tuple (systemId, directoryPath, (fileName))

    Validation that it points to a real resource is not implemented. The
    same caveats about validation apply here as in to_agave_uri()
    """
    systemId = None
    dirPath = None
    fileName = None

    proto = re.compile("s3:\/\/(.*)$")

    if uri is None:
        raise Exception("URI cannot be empty")
    resourcepath = proto.search(uri)
    if resourcepath is None:
        raise Exception("Unable resolve URI")
    resourcepath = resourcepath.group(1)

    firstSlash = resourcepath.find('/')
    if firstSlash is -1:
        raise Exception("Unable to resolve systemId")

    try:
        systemId = 'data-' + resourcepath[0:firstSlash]
        origDirPath = resourcepath[firstSlash + 1:]
        dirPath = '/' + os.path.dirname(origDirPath)
        fileName = os.path.basename(origDirPath)
        if fileName is '':
            fileName = '/'
    except Exception as e:
        raise Exception(
            "Error resolving directory path or file name: {}".format(e))

    return(systemId, dirPath, fileName)


def from_agave_uri(uri=None, Validate=False):
    """
    Parse an Agave URI into a tuple (systemId, directoryPath, fileName)

    Validation that it points to a real resource is not implemented. The
    same caveats about validation apply here as in to_agave_uri()
    """
    systemId = None
    dirPath = None
    fileName = None

    proto = re.compile("agave:\/\/(.*)$")

    if uri is None:
        raise Exception("URI cannot be empty")
    resourcepath = proto.search(uri)
    if resourcepath is None:
        raise Exception("Unable resolve URI")
    resourcepath = resourcepath.group(1)

    firstSlash = resourcepath.find('/')
    if firstSlash is -1:
        raise Exception("Unable to resolve systemId")

    try:
        systemId = resourcepath[0:firstSlash]
        origDirPath = resourcepath[firstSlash + 1:]
        dirPath = '/' + os.path.dirname(origDirPath)
        fileName = os.path.basename(origDirPath)
        if fileName is '':
            fileName = '/'
    except Exception as e:
        raise Exception(
            "Error resolving directory path or file name: {}".format(e))

    return(systemId, dirPath, fileName)


"""
https://api.sd2e.org/files/v2/media/system/data-sd2e-projects-users//vaughn/jupyter-agave-test/exp2801-04-ds731218.msf
https://api.sd2e.org/files/v2/download/vaughn/system/data-sd2e-community/sample/jupyter/notebooks/meslami-SD2_Quicklooks_Combined_v4.ipynb
"""
def agave_uri_from_http(httpURI=None):
    """
    Convert an HTTP(s) URI to its agave:// format
    * Do not use yet
    """
    agaveURI = None
    proto = re.compile("http(s)?:\/\/(.*)$")
    resourcePath = proto.search(httpURI)
    if resourcePath is None:
        raise ValueError('Unable resolve ' + httpURI)
    resourcePath = resourcePath.group(2)
    elements = resourcePath.split('/')
    elements = list(filter(None, elements))
    apiServer, apiEndpoint, systemId = (elements[0], elements[1], None)
    if '/download/' in resourcePath:
        systemId = elements[6]
        sysPath = '/'.join(elements[7:])
    elif '/media/' in resourcePath:
        systemId = elements[5]
        sysPath = '/'.join(elements[6:])

    agaveURI = 'agave://{}/{}'.format(systemId, sysPath)
    return agaveURI


# TODO - Formalize how to acquire tenant api server and username. Will
#        require having an active Agave client
def http_uri_from_agave(agaveURI=None, linkType='media', userName='public'):
    """
    Returns an http(s) media URL for data movement or download
    * Do not use yet.
    """
    httpURI = None

    typeSlug = '/'

    if linkType not in FILES_HTTP_LINK_TYPES:
        raise ValueError('linkType ' + linkType + ' not a valid value')
    elif linkType == 'media':
        typeSlug = 'media/'
    else:
        typeSlug = 'download/' + userName + '/'

    systemId, dirPath, fileName = from_agave_uri(agaveURI)
    httpURI = 'https://api.tacc.cloud/files/v2/' + typeSlug + \
        'system/' + systemId + '/' + dirPath + fileName
    return httpURI

# Normally, one can just inspect her API client to get these values
# but because Abaco creates ephemeral API clients using impersonation
# it's not always perfectly possible. These functions consult the
# local Abaco runtime context before trying heroically to pull the
# values out of the API client itself. This should preserve our ability
# to debug locally while still being able to access these three essential
# values from within Abaco functions.


def get_api_server(ag):
    '''Get current API server URI'''
    if os.environ.get('_abaco_api_server'):
        return os.environ.get('_abaco_api_server')
    elif ag.token is not None:
        try:
            return ag.token.api_server
        except Exception as e:
            print("ag.token was None: {}".format(e))
            pass
        return None
    else:
        print("Used hard-coded value for API server")
        return None


def get_api_token(ag):
    '''Get API access_token'''
    if os.environ.get('_abaco_access_token'):
        return os.environ.get('_abaco_access_token')
    elif ag.token is not None:
        try:
            return ag.token.token_info.get('access_token')
        except Exception as e:
            print("ag.token was None: {}".format(e))
            pass
        return None
    else:
        print("Failed to retriev API access_token")
        return ""


def get_api_username(ag):
    '''Get current API username'''
    if os.environ.get('_abaco_username'):
        return os.environ.get('_abaco_username')
    elif ag is not None:
        try:
            return ag.username
        except Exception as e:
            print("ag was None: {}".format(e))
        return None
    else:
        print("No username could be determined")
        return None
