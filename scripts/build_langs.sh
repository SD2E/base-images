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

CHANNEL="stable"
CHANNELTAG=""
if [ "${RELEASE}" != "stable" ]; then
    CHANNELTAG="-${RELEASE}"
    CHANNEL="${RELEASE}"
fi

if [ "$LANGUAGE" == "python" ]; then
    LANGVERSIONS="python2 python3"
elif [ ! -z "$LANGUAGE" ]; then
    LANGVERSIONS=${LANGUAGE}
else
    LANGVERSIONS="python2 python3 java8"
fi

if [ ! -z "${DIST}" ]
then
    DISTVERSIONS="${DIST}"
else
    DISTVERSIONS="ubuntu16 ubuntu17"
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
            echo "  Building ${TENANT_DOCKER_ORG}/${LANG}:${VERSION}${CHANNELTAG}"

            DOCKERFILE="Dockerfile.${VERSION}${CHANNELTAG}"
            if [ "${CHANNELTAG}" != "stable" ] && [ ! -f "$DOCKERFILE" ]; then
                echo "$DOCKERFILE for channel ${CHANNELTAG} not found. Using stable version."
                DOCKERFILE="Dockerfile.${VERSION}"
            fi

            if [ -f "${DOCKERFILE}" ]; then
                bash $DIR/docker_helper.sh "${TENANT_DOCKER_ORG}/${LANG}" "${VERSION}${CHANNELTAG}" "${DOCKERFILE}" "${COMMAND}"
            else
                echo "${DOCKERFILE} not found. Skipped."
            fi
        done
        cd ${OWD}
    else
        echo "${LANG} not found. Skipped."
    fi
done
