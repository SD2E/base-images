
.PHONY: all tests
.SILENT: all tests
all: image
	true

sdk: sdk-clean
	cp -R ../sdk/python/* .

tests: clean sdk
	bash tests/run-container-tests.sh

sdk-clean:
	rm -rf tests
	rm -rf reactors
	rm -rf abacoschemas

clean: sdk-clean
	rm -rf .hypothesis .pytest_cache */__pycache__ reactor.log *.pyc
