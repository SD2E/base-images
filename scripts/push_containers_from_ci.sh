#!/usr/bin/env bash

REG=$1
CHANNEL=$2

TAG=
if [ "${CHANNEL}" == "edge" ]; then
    TAG="-edge"
else
    TAG=""
fi

for IMG in `docker images -f "reference=${REG}/*${TAG}" | grep -v REPOSITORY | awk '{ print $1":"$2 }'`
do
    echo "Pushing $IMG"
    docker push ${IMG}
done
