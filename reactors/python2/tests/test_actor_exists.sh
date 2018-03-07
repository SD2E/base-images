#!/usr/bin/env bash

ACTOR_ID=$1
if [ -z "${ACTOR_ID}" ]
then
    echo "Usage: $(basename $0) [ACTORID]"
    exit 1
fi

RESPONSE=$(abaco list -v ${ACTOR_ID} | jq -r .status)
if [ "${RESPONSE}" == "success" ]
then
    echo "Actor ${ACTOR_ID} found"
    exit 0
else
    echo "Error or Actor ${ACTOR_ID} not found"
    exit 1
fi
