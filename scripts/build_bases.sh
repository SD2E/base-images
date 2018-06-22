#!/usr/bin/bash

if [[ -z "${DIR}" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

# mandatory
TENANT_DOCKER_ORG=$1
RELEASE=$2
COMMAND=$3
# optional
DIST=$4

CHANNEL="stable"
CHANNELTAG=""
if [ "${RELEASE}" != "stable" ]; then
    CHANNELTAG="-${RELEASE}"
    CHANNEL="${RELEASE}"
fi

if [ ! -z "${DIST}" ]
then
    DISTVERSIONS="${DIST}"
else
    DISTVERSIONS="alpine36 centos7 ubuntu16 ubuntu17 miniconda3 miniconda2"
fi

echo "** CONFIG **"
echo "Command: ${COMMAND} | Channel: ${RELEASE}"
echo "Languages: NA"
echo "Distributions: ${DISTVERSIONS}"
echo "Building..."

OWD=${PWD}
cd ${DIR}/../base
for VERSION in ${DISTVERSIONS}
do
    DOCKERFILE="Dockerfile.${VERSION}${CHANNELTAG}"
    if [ "${CHANNELTAG}" != "stable" ] && [ ! -f "$DOCKERFILE" ]; then
        echo "$DOCKERFILE for channel ${CHANNELTAG} not found. Using stable version."
        DOCKERFILE="Dockerfile.${VERSION}"
    fi
    if [ -f "${DOCKERFILE}" ]; then
        echo "Building ${TENANT_DOCKER_ORG}/base:${VERSION}${CHANNELTAG}"
        bash ${DIR}/docker_helper.sh "${TENANT_DOCKER_ORG}/base" "${VERSION}${CHANNELTAG}" "${DOCKERFILE}" "${COMMAND}"
    else
        echo "${DOCKERFILE} not found. Skipped."
    fi
done
cd ${OWD}
