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

CHANNEL=""
if [ "$RELEASE" != "stable" ]; then
    CHANNEL="-${RELEASE}"
fi

if [ ! -z "$LANGUAGE" ]
then
    LANGVERSIONS="$LANGUAGE"
else
    LANGVERSIONS="python2 python3 bash ruby golang"
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
        if [ -f "Dockerfile${CHANNEL}" ]; then
            bash $DIR/docker_helper.sh "${TENANT_DOCKER_ORG}/reactors" "${VERSION}${CHANNEL}" "Dockerfile${CHANNEL}" "${COMMAND}"
            cd $DIR/../reactors
        else
            echo "Dockerfile${CHANNEL} for ${VERSION} not found. Skipped."
        fi
    else
        echo "${VERSION} not found. Skipped."
    fi
done
cd $OWD
