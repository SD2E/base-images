#!/usr/bin/env bash

REG=$1
IMAGE=$2
TAG=$3
CHANNEL=$4

SUFFIX=
if [ "${CHANNEL}" == "edge" ]; then
    SUFFIX="-edge"
else
    SUFFIX=""
fi

for IMG in `docker images -f "reference=${REG}/${IMAGE}:${TAG}${SUFFIX}" | grep -v REPOSITORY | awk '{ print $1":"$2 }'`
do
    echo "Pushing $IMG"
    docker push ${IMG}
done
