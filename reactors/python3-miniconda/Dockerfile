FROM sd2e/python3:miniconda

ARG CHANNEL=edge
ARG LANGUAGE=python3-miniconda
ARG VERSION=0.8.1
ARG SCRATCH=/mnt/ephemeral-01
ARG AGAVEPY_BRANCH=master
ARG DATACATALOG_BRANCH=master

# Discoverable version inside the container
RUN echo "TACC.cloud Reactors\nLanguage: ${LANGUAGE}\nVersion: ${VERSION}" > /etc/reactors-VERSION
# Helpful env variable
ENV REACTORS_VERSION=${VERSION}
ENV SCRATCH=${SCRATCH}

# This is a container-local directory
# that all UIDs can write to. It will
# of course, not survive when
# the container is torn down.
#
# Other entries in /mnt/ will
# be various types of persistent
# storage

RUN mkdir -p ${SCRATCH} && \
    chmod a+rwx ${SCRATCH} && \
    chmod g+rwxs ${SCRATCH}
ENV _REACTOR_TEMP=${SCRATCH}

# Install components from Python SDK, which is still maintained in the
# base-images repo, but is being prepared to move to a standalone
# repository

# The main client-side SDK. Adds extended capability and utility functions
# to the Python runtime.
ADD sdk/reactors /reactors

# Default files that turn the reactors:pythonX image into
# a viable Reactor on its own. Implements a trival "Hello World" that
# exercises key aspects of the platform.
ADD reactor.py /
ADD sdk/config.yml /
ADD sdk/abacoschemas /abacoschemas
# Older builds used message.json as an example message,
# for the purpose of instruction. Later (post 2/2018) use message.jsonschema
# to provide the default schema for JSON messages to the Reactor.
ADD sdk/message.json* /message.jsonschema

# Force locale to UTF-8
RUN apt-get update && \
    apt-get install -y locales locales-all && \
    apt-get clean
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install additional requirements from SDK
ADD sdk/requirements-${CHANNEL}.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt

# Track to latest AgavePy
# RUN pip3 install git+https://github.com/TACC/agavepy.git@${AGAVEPY_BRANCH}

# # Track to latest SD2 datacatalog
# RUN pip3 install --upgrade git+https://github.com/SD2E/python-datacatalog.git@${DATACATALOG_BRANCH}

CMD ["python3", "/reactor.py"]

# Onbuild support
ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN pip3 install -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
ONBUILD ADD message.json* /message.jsonschema

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
