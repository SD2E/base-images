#!/usr/bin/env bash

ACTOR_ID=$1
MESSAGE="You have to be a bit of a liar to tell a story the right way."

if [ -z "${ACTOR_ID}" ]
then
    echo "Usage: $(basename $0) [ACTORID]"
    exit 1
fi

MAX_ELAPSED=100 # Maximum duration for any async task
INITIAL_PAUSE=1 # Initial delay
BACKOFF=2 # Exponential backoff

TS1=$(date "+%s")
TS2=
ELAPSED=0
PAUSE=${INITIAL_PAUSE}
JOB_STATUS=
EXEC_ID=$(abaco run -v -m "${MESSAGE}" ${ACTOR_ID} | jq -r .result.executionId)
echo -n "Execution $EXEC_ID"
while [ "${JOB_STATUS}" != "COMPLETE" ]
do
    TS2=$(date "+%s")
    ELAPSED=$((${TS2} - ${TS1}))
    JOB_STATUS=$(abaco executions -v -e ${EXEC_ID} ${ACTOR_ID} | jq -r .result.status)
    if [ "${ELAPSED}" -gt "${MAX_ELAPSED}" ]
    then
        break
    fi
    printf "Wait " ; printf "%0.s." $(seq 1 ${PAUSE}); printf "\n"
    sleep $PAUSE
    PAUSE=$(($PAUSE * $BACKOFF))
done
echo " ${ELAPSED} seconds"

if [ "${JOB_STATUS}" == "COMPLETE" ]
then
    abaco logs -e ${EXEC_ID} ${ACTOR_ID}
    exit 0
else
    echo "Error or Actor ${ACTOR_ID} couldn't process message"
    exit 1
fi
