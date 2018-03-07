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

CHANNEL=""
if [ "${RELEASE}" != "stable" ]; then
    CHANNEL="-${RELEASE}"
fi

if [ ! -z "${DIST}" ]
then
    DISTVERSIONS="${DIST}"
else
    DISTVERSIONS="alpine36 ubuntu16 ubuntu17"
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
    if [ -f "Dockerfile.${VERSION}${CHANNEL}" ]; then
        echo "Building ${TENANT_DOCKER_ORG}/base:${VERSION}${CHANNEL}"
        bash ${DIR}/docker_helper.sh "${TENANT_DOCKER_ORG}/base" "${VERSION}${CHANNEL}" "Dockerfile.${VERSION}${CHANNEL}" "${COMMAND}"
    else
        echo "Dockerfile.${VERSION}${CHANNEL} not found. Skipped."
    fi
done
cd ${OWD}
