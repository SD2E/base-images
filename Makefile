include config.mk

CHANNEL := "stable"
TENANT_NAME := $(TENANT_NAME)
TENANT_ID := $(TENANT_KEY)
TENANT_DOCKER_ORG := $(TENANT_DOCKER_ORG)
PREFIX := $(HOME)

OBJ := $(MAKE_OBJ)
TARGETS = base languages

.SILENT: test
test:
	echo "Not implemented"

help:
	echo "You can make base, languages, apps, reactors, clean"

base-build:
	bash scripts/build_bases.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

base: base-build
	bash scripts/build_bases.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

lang-build:
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

languages: lang-build
	bash scripts/build_langs.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

apps-build:
	bash scripts/build_apps.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

apps: apps-build
	bash scripts/build_apps.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

jupyter-build:
	bash scripts/build_jupyter.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

jupyter: jupyter-build
	bash scripts/build_jupyter.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

reactors-build:
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) $(CHANNEL) build

reactors: reactors-build
	bash scripts/build_reactors.sh $(TENANT_DOCKER_ORG) $(CHANNEL) release

