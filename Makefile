include config.mk

CHANNEL := stable
BASE := ""
LANGUAGE := ""

TENANT_NAME := $(TENANT_NAME)
TENANT_ID := $(TENANT_KEY)
TENANT_DOCKER_ORG := $(TENANT_DOCKER_ORG)
PREFIX := $(HOME)

BUILDS = base-build language-build apps-build jupyter-build reactors-build
IMAGES = base language apps jupyter reactors

.SILENT: test

help:
	echo "You can make base, language, apps, reactors, clean"

all: images
	true

builds: $(BUILDS)
	true

images: $(IMAGES)
	true

tests:
	echo "Not implemented"

base-build:
	bash scripts/build_bases.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(BASE)

base: base-build
	bash scripts/build_bases.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(BASE)

language-build:
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(LANGUAGE) $(BASE)

language: language-build
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(LANGUAGE) $(BASE)

apps-build: language-build
	bash scripts/build_apps.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(LANGUAGE) $(BASE)

apps: apps-build
	bash scripts/build_apps.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(LANGUAGE) $(BASE)

jupyter-build: base-build
	bash scripts/build_jupyter.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

jupyter: jupyter-build
	bash scripts/build_jupyter.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

reactors-build:
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(LANGUAGE)

reactors: reactors-build
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(LANGUAGE)

