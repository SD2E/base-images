#!/usr/bin/bash

TENANT_DOCKER_ORG=$1
RELEASE=$2
COMMAND=$3

CHANNEL=""
if [ "$RELEASE" != "stable" ]; then
    CHANNEL="-${RELEASE}"
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

echo "Building reactors images..."
OWD=$PWD
cd $DIR/../reactors
for VERSION in "python2" "python3"
do
    echo "Building $TENANT_DOCKER_ORG/reactors:${VERSION}"
    cd $DIR/../reactors/$VERSION
    if [ -f "Dockerfile${CHANNEL}" ]; then
        bash $DIR/docker_helper.sh "${TENANT_DOCKER_ORG}/reactors" "${VERSION}${CHANNEL}" "Dockerfile${CHANNEL}" "${COMMAND}"
    cd $DIR/../reactors
    fi
done
cd $OWD
