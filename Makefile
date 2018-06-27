include config.mk

CHANNEL := stable
BASE := ""
LANGUAGE := ""

TENANT_NAME := $(TENANT_NAME)
TENANT_ID := $(TENANT_KEY)
TENANT_DOCKER_ORG := $(TENANT_DOCKER_ORG)
TENANT_GITHUB_ORG := $(TENANT_GITHUB_ORG)
TENANT_TRAVIS_ORG := $(TENANT_TRAVIS_ORG)

PREFIX := $(HOME)

BUILDS = base-build languages-build apps-build jupyter-build reactors-build
IMAGES = base languages reactors apps

.SILENT: test

help:
	echo "You can make base, languages, apps, reactors, clean"

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

languages-build:
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(LANGUAGE) $(BASE)

languages: languages-build
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(LANGUAGE) $(BASE)

apps-build:
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

reactors-edge:
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) edge build python
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) edge release python

reactors-clean:
	cd reactors/python2 ; \
	make clean
	cd reactors/python3 ; \
	make clean
	cd reactors/python2-miniconda ; \
	make clean
	cd reactors/python3-miniconda ; \
	make clean

downstream:
	scripts/trigger-travis.sh $(TENANT_GITHUB_ORG) base-images-custom $(TRAVIS_ACCESS_TOKEN)
