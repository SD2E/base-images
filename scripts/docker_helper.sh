#!/bin/bash

IMAGE=$1
TAG=$2
DOCKERFILE=$3
COMMAND=$4

echo "Command: $COMMAND"

function die {

    die "$1"
    exit 1

}


DOCKER_INFO=`docker info > /dev/null`
if [ $? -ne 0 ] ; then die "Docker not found or unreachable. Exiting." ; fi

if [[ "$COMMAND" == 'build' ]];
then

buildopts=""
if [ "$NO_REMOVE" == 1 ]; then
    buildopts="$buildopts --rm=false"
fi
if [ "$NO_CACHE" == 1 ]; then
    buildopts="$buildopts --no-cache"
fi
if [ ! -z "$CHANNEL" ]; then
    buildopts="$buildopts --no-cache --build-arg CHANNEL=${CHANNEL}"
fi
if [ "$DOCKER_PULL" == 1 ]; then
    buildopts="$buildopts --pull --no-cache --build-arg CHANNEL=${CHANNEL}"
fi

echo "Image: $IMAGE"
echo "Tag: $TAG"
echo "Dockerfile: $DOCKERFILE"
echo "Command: $COMMAND"
echo "Build Opts: ${buildopts}"

docker build ${buildopts} -t ${IMAGE}:${TAG} -f ${DOCKERFILE} .
if [ $? -ne 0 ] ; then die "Error on build. Exiting." ; fi

IMAGEID=`docker images -q  ${IMAGE}:${TAG}`
if [ $? -ne 0 ] ; then die "Can't find image ${TENANT_DOCKER_ORG}/${IMAGE}:${TAG}. Exiting." ; fi

# docker tag ${IMAGEID} ${IMAGE}:latest
# if [ $? -ne 0 ] ; then die "Error tagging with 'latest'. Exiting." ; fi

fi


if [[ "$COMMAND" == 'release' ]];
then

docker push ${IMAGE}:${TAG}

if [ $? -ne 0 ] ; then die "Error pushing to Docker Hub. Exiting." ; fi
fi


if [[ "$COMMAND" == 'clean' ]];
then

docker rmi -f ${IMAGE}:${TAG} && docker rmi -f ${IMAGE}:latest

if [ $? -ne 0 ] ; then die "Error deleting local images. Exiting." ; fi
fi
