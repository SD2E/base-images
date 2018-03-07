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

echo "Not implemented" && exit 0
