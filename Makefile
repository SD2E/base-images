ACTOR_ID ?= $(shell head -1 .actorid)
AGAVE_CREDS ?= ~/.agave
GITREF=$(shell git rev-parse --short HEAD)
GITREF_FULL=$(shell git rev-parse HEAD)

# lightweight JSON to env utility, as string
define JSON_TO_ENV
import json as j, pipes as p, sys as s;
[print('{0}={1};'.format(p.quote(k), p.quote(v))) for k, v in j.load(s.stdin).items()]
endef
export JSON_TO_ENV

# ------------------------------------------------------------------------------
# Sanity checks
# ------------------------------------------------------------------------------

PROGRAMS := git docker python poetry singularity tox tapis
.PHONY: $(PROGRAMS)
.SILENT: $(PROGRAMS)

docker:
	docker info 1> /dev/null 2> /dev/null && \
	if [ ! $$? -eq 0 ]; then \
		echo "\n[ERROR] Could not communicate with docker daemon. You may need to run with sudo.\n"; \
		exit 1; \
	fi
python poetry singularity tapis:
	$@ --help &> /dev/null; \
	if [ ! $$? -eq 0 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please install $@"; \
		exit 1; \
	fi
tox:
	$@ -h &> /dev/null; \
	if [ ! $$? -eq 0 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please pip install $@"; \
		exit 1; \
	fi
git:
	$@ -h &> /dev/null; \
	if [ ! $$? -eq 129 ]; then \
		echo "[ERROR] $@ does not seem to be on your path. Please install $@"; \
		exit 1; \
	fi

# ------------------------------------------------------------------------------

tests: secrets.json | tapis docker
	tapis actors deploy
	sleep 5
	tapis actors run -m 'my message' -e 'test_context_key=test_context_value' $$(cat .actorid)

tests-local: .env | docker tapis
	# Build image using Tapis CLI and retrieve the image hash
	@# TODO: find a less hacky way to do this
	$(eval IMAGE = $(shell tapis actors deploy -R -f json 2>/dev/null | \
		jq -r '.[].message|select(startswith("Successfully built"))' | \
		awk '{print $$3}'))
	docker run --rm -it --env-file $^ -v $(AGAVE_CREDS):/root/.agave $(IMAGE)

secrets.json:
	if [ ! -f $@ ]; then \
		echo '{"dont_reveal": "secret_value"}' > $@; \
	fi

.env: secrets.json | python
	cat $^ | python -c "$${JSON_TO_ENV}" > $@
