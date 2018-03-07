#!/usr/bin/bash

TENANT_DOCKER_ORG=$1
RELEASE=$2
COMMAND=$3

CHANNEL=""
if [ "$RELEASE" != "stable" ]; then
    CHANNEL="-${CHANNEL}"
fi

if [ -z "$COMMAND" ]; then
    COMMAND="build"
fi

if [[ -z "$DIR" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

echo "Command: $COMMAND | Channel: $RELEASE"

if [[ -z "$DIR" ]]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

echo "Building base images..."
OWD=$PWD
cd $DIR/../base
for VERSION in alpine36 ubuntu14 ubuntu16 ubuntu17 ubuntu18
do
    echo "Building $TENANT_DOCKER_ORG/base:${VERSION}"
    if [ -f "Dockerfile.${VERSION}" ]; then
        bash $DIR/docker_helper.sh "$TENANT_DOCKER_ORG/base" "${VERSION}${CHANNEL}" "Dockerfile.${VERSION}" "${COMMAND}"
    fi
done
cd $OWD
