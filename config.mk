PYTHON ?= python3
AGAVE_CRED_CACHE ?= ~/.agave
DOCKER_ORG ?= sd2etest
DOCKER_REPO ?= reactors
DOCKER_TAG ?= python3
DOCKER_IMAGE ?= $(DOCKER_ORG)/$(DOCKER_REPO):$(DOCKER_TAG)
