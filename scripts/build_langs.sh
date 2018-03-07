#!/usr/bin/env bash

if [[ -z "${DIR}" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

# mandatory
TENANT_DOCKER_ORG=$1
RELEASE=$2
COMMAND=$3
# optional
LANGUAGE=$4
DIST=$5

CHANNEL=""
if [ "${RELEASE}" != "stable" ]; then
    CHANNEL="-${RELEASE}"
fi

if [ ! -z "${LANGUAGE}" ]
then
    LANGVERSIONS="${LANGUAGE}"
else
    LANGVERSIONS="python2 python3"
fi

if [ ! -z "${DIST}" ]
then
    DISTVERSIONS="${DIST}"
else
    DISTVERSIONS="alpine36 ubuntu16 ubuntu17"
fi

echo "** CONFIG **"
echo "Command: ${COMMAND} | Channel: ${RELEASE}"
echo "Languages: ${LANGVERSIONS}"
echo "Distributions: ${DISTVERSIONS}"
echo "Building..."

OWD=${PWD}
for LANG in ${LANGVERSIONS}
do
    if [ -d "${DIR}/../languages/${LANG}" ]; then
        echo "Building ${TENANT_DOCKER_ORG}/${LANG}:*"
        cd ${DIR}/../languages/${LANG}
        for VERSION in ${DISTVERSIONS}
        do
            echo "  Building ${TENANT_DOCKER_ORG}/${LANG}:${VERSION}${CHANNEL}"
            if [ -f "Dockerfile.${VERSION}${CHANNEL}" ]; then
                bash $DIR/docker_helper.sh "${TENANT_DOCKER_ORG}/${LANG}" "${VERSION}${CHANNEL}" "Dockerfile.${VERSION}${CHANNEL}" "${COMMAND}"
            else
                echo "Dockerfile.${VERSION}${CHANNEL} not found. Skipped."
            fi
        done
        cd ${OWD}
    else
        echo "${LANG} not found. Skipped."
    fi
done
