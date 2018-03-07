include config.mk

CHANNEL := "stable"
BASE := ""
LANGUAGE := ""
REACTOR := ""

TENANT_NAME := $(TENANT_NAME)
TENANT_ID := $(TENANT_KEY)
TENANT_DOCKER_ORG := $(TENANT_DOCKER_ORG)
PREFIX := $(HOME)

BUILDS = base-build languages-build apps-build jupyter-build reactors-build
IMAGES = base languages apps jupyter reactors

.SILENT: test
test:
	echo "Not implemented"

help:
	echo "You can make base, languages, apps, reactors, clean"

builds: $(BUILDS)
	true

images: $(IMAGES)
	true

base-build:
	bash scripts/build_bases.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(BASE)

base: base-build
	bash scripts/build_bases.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(BASE)

languages-build:
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(LANGUAGE) $(BASE)

languages: languages-build
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(LANGUAGE) $(BASE) 

apps-build:
	bash scripts/build_apps.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

apps: apps-build
	bash scripts/build_apps.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

jupyter-build:
	bash scripts/build_jupyter.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

jupyter: jupyter-build
	bash scripts/build_jupyter.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

reactors-build:
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build $(LANGUAGE)

reactors: reactors-build
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release $(LANGUAGE)

