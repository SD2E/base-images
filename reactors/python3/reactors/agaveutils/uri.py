"""
Functions for working with Agave, HTTP, and TACC S3 URIs
"""
import re
import os
import time
from agavepy.agave import Agave, AgaveError


MAX_ELAPSED = 300
MAX_RETRIES = 5
FILES_HTTP_LINK_TYPES = ('media', 'download')


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
        # if fileName is '':
        #     fileName = '/'
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
    elements = list([_f for _f in elements if _f])
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
