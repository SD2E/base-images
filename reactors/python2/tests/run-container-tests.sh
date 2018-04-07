#!/usr/bin/env bash

# Invoke code for a Reactor in an environment
# that closely emulates the Abaco runtime

# Required Globals
#   None
# Optional Globals
#   REACTOR_RC
#   REACTOR_RUN_OPTS
#   REACTOR_USE_TMP
#   REACTOR_CLEANUP_TMP
#   REACTOR_LOCAL
#   CONTAINER_REPO
#   CONTAINER_TAG
#   AGAVE_CACHE_DIR
#   REACTOR_JOB_DIR
#
# Required input
#   MESSAGE - File containing JSON message body
# Optional
#   CONFIG - Reactor config file (reactor.rc)
#

#COMMANDS="$@"
COMMAND="pytest -s -vvv"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/common.sh"

CONTAINER_IMAGE="python2-test-mwv"
# CONTAINER_IMAGE="$(basename $(dirname ${DIR}))-$(date +%s)"

docker build -t $CONTAINER_IMAGE .

# Api integration
AGAVE_CRED="${AGAVE_CACHE_DIR}"
if [ ! -d "${AGAVE_CRED}" ]; then
    AGAVE_CRED="${HOME}/.agave"
fi
if [ ! -f "${AGAVE_CRED}/current" ]; then
    die "No API credentials found in ${AGAVE_CRED}"
fi

# Emphemeral directory
#  Can be specified with REACTOR_JOB_DIR
#  Can be turned off with REACTOR_NO_TMP=1
WD=${PWD}
TEMP=""
if ((REACTOR_USE_TMP )); then
    if [ ! -z "${REACTOR_JOB_DIR}" ]; then
        rm -rf "${REACTOR_JOB_DIR}";
        mkdir -p "${REACTOR_JOB_DIR}"
        TEMP=${REACTOR_JOB_DIR}
    else
        TEMP=`mktemp -d $PWD/tmp.XXXXXX`
    fi
    WD=${TEMP}
fi
log "Working directory: ${WD}"

# Volume mounts
MOUNTS="-v ${WD}:/mnt/ephemeral-01"
if [ -d "${AGAVE_CACHE_DIR}" ]; then
    MOUNTS="$MOUNTS -v ${AGAVE_CACHE_DIR}:/root/.agave:rw"
fi

envopts=""
if ((REACTOR_LOCAL)); then
    envopts="${envopts} -e LOCALONLY=1"
fi

# Tweak config for Docker depending on if we're running under CI
dockeropts="${REACTOR_RUN_OPTS}"
detect_ci
if ((UNDER_CI)); then
  # If running a Dockerized process with a volume mount
  # written files will be owned by root and unwriteable by
  # the CI user. We resolve this by setting the group, which
  # is the same approach we use in the container runner
  # that powers container-powered Agave jobs
  dockeropts=" --user=0:${CI_GID}"
fi

docker run -t ${dockeropts} ${envopts} ${MOUNTS} ${CONTAINER_IMAGE} $COMMAND

# docker rmi -f ${CONTAINER_IMAGE}

# # Clean up: Set permissions and ownership on volume mount
# if ((UNDER_CI)); then
#     docker run ${dockeropts} -t -v ${WD}:/mnt/ephemeral-01 -w /mnt/ephemeral-01 ${CONTAINER_IMAGE} find . -type d -exec chmod 0777 {} \;
#     docker run ${dockeropts} -t -v ${WD}:/mnt/ephemeral-01 -w /mnt/ephemeral-01 ${CONTAINER_IMAGE} find . -type f -exec chmod 0666 {} \;
#     docker run ${dockeropts} -t -v ${WD}:/mnt/ephemeral-01 -w /mnt/ephemeral-01 ${CONTAINER_IMAGE} find . -exec chown ${CI_UID}:${CI_GID} {}
#     if ((REACTOR_CLEANUP_TMP)) && [ -z "${TEMP}" ]; then
#         log "Cleaning up ${TEMP}"
#         rm -rf ${TEMP}
#     fi
# fi
