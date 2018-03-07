#!/usr/bin/env bash

ACTOR_ID=$1
if [ -z "${ACTOR_ID}" ]
then
    echo "Usage: $(basename $0) [ACTORID]"
    exit 1
fi

MAX_ELAPSED=100 # Maximum duration for any async task
INITIAL_PAUSE=0.500 # Initial delay. Don't make smaller than 0.5s for now
BACKOFF=1.10 # Progressive backoff rate (10%)

# Verify that the Reactor has been created
echo -n "Validating actor: "
TS1=$(date "+%s")
TS2=
ELAPSED=0
PAUSE=${INITIAL_PAUSE}
ACTOR_STATUS=

while [ "${ACTOR_STATUS}" != "READY" ]
do
    TS2=$(date "+%s")
    ELAPSED=$((${TS2} - ${TS1}))
    ACTOR_STATUS=$(abaco list -v ${ACTOR_ID} | jq -r .result.status)
    echo -n "."
    if [ "${ELAPSED}" -gt "${MAX_ELAPSED}" ]
    then
        break
    fi
    sleep ${PAUSE}
    PAUSE=$(echo "${PAUSE}*${BACKOFF}" | bc)
done
echo " ${ELAPSED} sec"

if [ "${ACTOR_STATUS}" == "READY" ]
then
    echo "Actor ${ACTOR_ID} ready."
    exit 0
else
    echo "Error or Actor ${ACTOR_ID} not ready"
    exit 1
fi
