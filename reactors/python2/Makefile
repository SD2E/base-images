API_TOKEN = $(shell jq -r .access_token $(HOME)/.agave/current)
API_URL = $(shell jq -r .baseurl $(HOME)/.agave/current)

include reactor.mk

.PHONY: all
.SILENT: all
all: image
	true

.PHONY: develop
.SILENT: develop
develop: reactor tests
	true

.PHONY: help
.SILENT: help
help:
	echo "You can make the following targets:"
	make -rpn | sed -n -e '/^$$/ { n ; /^[^ .#][^ ]*:/ { s/:.*$$// ; p ; } ; }' | sort -k1

.PHONY: info
.SILENT: info
info: config-info reactor-info
	true

.PHONY: config-info
.SILENT: config-info
config-info:
	echo "api: $(API_URL)"
	echo "token: $(API_TOKEN)"
	echo "image: $(DOCKER_HUB_ORG)/$(DOCKER_IMAGE_TAG)$(DOCKER_IMAGE_VERSION)"

.PHONY: reactor-info
.SILENT: reactor-info
reactor-info:
	echo "************************"
	echo "Name: $(REACTOR_NAME)" && \
	echo "ID: $(shell cat ACTOR_ID)"
	
.PHONY: image
.SILENT: image
image: docker-build docker-push
	echo "image: $(DOCKER_HUB_ORG)/$(DOCKER_IMAGE_TAG)$(DOCKER_IMAGE_VERSION)"

.PHONY: reactor
.SILENT: reactor
reactor: image reactor-create reactor-info
	true

.PHONY: docker-build
.SILENT: docker-build
docker-build:
	docker build -t $(DOCKER_HUB_ORG)/$(DOCKER_IMAGE_TAG)$(DOCKER_IMAGE_VERSION) .

.PHONY: docker-push
.SILENT: docker-push
docker-push:
	docker push $(DOCKER_HUB_ORG)/$(DOCKER_IMAGE_TAG)$(DOCKER_IMAGE_VERSION)
	touch .pushed

.SILENT: reactor-create
reactor-create: .pushed
	set +x && \
	abaco create -f -v -n $(REACTOR_NAME) $(DOCKER_HUB_ORG)/$(DOCKER_IMAGE_TAG)$(DOCKER_IMAGE_VERSION) | jq -r .result.id > ACTOR_ID

.SILENT: tests
.PHONY: tests
tests: ACTOR_ID
	tests/test_actor_exists.sh $(shell cat ACTOR_ID) && \
	tests/test_actor_ready.sh $(shell cat ACTOR_ID) && \
	tests/test_actor_message.sh $(shell cat ACTOR_ID) && \
	echo "Tests complete"

.PHONY: pristine
.SILENT: pristine
pristine: clean
	abaco delete $(shell cat ACTOR_ID) && \
	rm -f ACTOR_ID

.PHONY: clean
.SILENT: clean
clean:
	rm -f .pushed .reactor.*
