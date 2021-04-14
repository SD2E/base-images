include config.mk
GITREF=$(shell git rev-parse --short HEAD)
GITREF_FULL=$(shell git rev-parse HEAD)

# ------------------------------------------------------------------------------
# Sanity checks
# ------------------------------------------------------------------------------

PROGRAMS := git docker $(PYTHON) poetry singularity tox tapis
.PHONY: $(PROGRAMS)
.SILENT: $(PROGRAMS)

docker:
	docker info 1> /dev/null 2> /dev/null && \
	if [ ! $$? -eq 0 ]; then \
		echo "\n[ERROR] Could not communicate with docker daemon.\n"; \
		exit 1; \
	fi
$(PYTHON) tapis:
	$@ --help &> /dev/null; \
	if [ ! $$? -eq 0 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please install $@"; \
		exit 1; \
	fi
git:
	$@ -h &> /dev/null; \
	if [ ! $$? -eq 129 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please install $@"; \
		exit 1; \
	fi

# ------------------------------------------------------------------------------
# Docker build
# ------------------------------------------------------------------------------

.PHONY: image

default_actor_context: | $(PYTHON)
	$(PYTHON) -m cookiecutter --no-input -c main --directory default -vf \
		https://github.com/TACC-Cloud/cc-tapis-v2-actors.git \
		name=$@ alias=$@

image: Dockerfile default_actor_context | docker
	docker build -f $< -t $(DOCKER_IMAGE) \
		--build-arg SDK_BRANCH=main \
		--build-arg PYTHON_VERSION=3.6.3 \
		--build-arg TEMPLATE_DIR="$(word 2, $^)" \
		.

tests: image | docker
	docker run --rm -v $(AGAVE_CRED_CACHE):/root/.agave $(DOCKER_IMAGE)

