#!/usr/bin/env bash

REG=$1

for IMG in `docker images ${REG}/* | grep -v REPOSITORY | awk '{ print $1":"$2 }'`
do
    echo "Pushing $IMG"
    docker push ${IMG}
done
