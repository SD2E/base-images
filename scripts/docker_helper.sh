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

echo "Image: $IMAGE"
echo "Tag: $TAG"
echo "Dockerfile: $DOCKERFILE"
echo "Command: $COMMAND"

docker build --rm=true -t ${IMAGE}:${TAG} -f ${DOCKERFILE} .
if [ $? -ne 0 ] ; then die "Error on build. Exiting." ; fi

IMAGEID=`docker images -q  ${IMAGE}:${TAG}`
if [ $? -ne 0 ] ; then die "Can't find image ${TENANT_DOCKER_ORG}/${IMAGE}:${TAG}. Exiting." ; fi

docker tag ${IMAGEID} ${IMAGE}:latest
if [ $? -ne 0 ] ; then die "Error tagging with 'latest'. Exiting." ; fi

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
