PYTESTDIR ?= "tests"
PYTESTOPTS ?= "-s -vvv"

all: sdk

sdk:
	cp -R ../sdk/python sdk

clean:
	rm -rf sdk .tox .coverage

tests: clean sdk
	cd sdk ; \
	PYTESTDIR="$(PYTESTDIR)" PYTESTOPTS="$(PYTESTOPTS)" make tests
