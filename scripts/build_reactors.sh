#!/usr/bin/bash

if [[ -z "$DIR" ]]; then
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

if [ ! -z "$LANGUAGE" ]
then
    LANGVERSIONS="$LANGUAGE"
else
    LANGVERSIONS="python2 python3 java8 bash ruby golang"
fi

if [ ! -z "$DIST" ]
then
    DISTVERSIONS="$DIST"
else
    DISTVERSIONS="alpine36 ubuntu16 ubuntu17"
fi

echo "** CONFIG **"
echo "Command: $COMMAND | Channel: $RELEASE"
echo "Languages: $LANGVERSIONS"
echo "Distributions: $DISTVERSIONS"
echo "Building..."

OWD=$PWD
cd ${DIR}/../reactors
for VERSION in ${LANGVERSIONS}
do
    if [ -d "${DIR}/../reactors/${VERSION}" ]; then
        echo "Building ${TENANT_DOCKER_ORG}/reactors:${VERSION}"
        cd ${DIR}/../reactors/${VERSION}

        DOCKERFILE="Dockerfile${CHANNELTAG}"
        if [ "${CHANNELTAG}" != "stable" ] && [ ! -f "$DOCKERFILE" ]; then
            echo "$DOCKERFILE for channel ${CHANNELTAG} not found. Using stable version."
            DOCKERFILE="Dockerfile"
        fi

        if [ -f "${DOCKERFILE}" ]; then
            bash $DIR/docker_helper.sh "${TENANT_DOCKER_ORG}/reactors" "${VERSION}${CHANNELTAG}" "${DOCKERFILE}" "${COMMAND}"
            cd $DIR/../reactors
        else
            echo "${DOCKERFILE} for ${VERSION} not found. Skipped."
        fi
    else
        echo "${VERSION} not found. Skipped."
    fi
done
cd $OWD
