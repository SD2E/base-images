PYTESTDIR ?= "tests"
PYTESTOPTS ?= "-s -vvv"

.PHONY: all tests
.SILENT: all tests

sdk:
	cp -R ../sdk/python/* .

shell:
	bash tests/run-container-tests.sh bash

tests:
	bash tests/run-container-tests.sh pytest ${PYTESTDIR} ${PYTESTOPTS}

clean: sdk-clean
	rm -rf .hypothesis .pytest_cache */__pycache__ reactor.log *.pyc
