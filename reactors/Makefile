PYTESTDIR ?= "tests"
PYTESTOPTS ?= "-s -vvv"

PYTHON_OBJ := python2 python3 python2-miniconda python3-miniconda

tests:
	for i in $(PYTHON_OBJ); do \
		cd $$i; \
		PYTESTDIR="$(PYTESTDIR)" PYTESTOPTS="$(PYTESTOPTS)" make tests; \
		cd ../ ; \
	done

clean:
	for i in $(PYTHON_OBJ); do \
		cd $$i; \
		make clean; \
		cd ../ ; \
	done
