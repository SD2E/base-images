FROM sd2e/python2:miniconda

ARG CHANNEL=stable
ARG LANGUAGE=python2-miniconda
ARG VERSION=0.8.1
ARG AGAVEPY_BRANCH=master
ARG AGAVEDB_BRANCH=master
ARG SCRATCH=/mnt/ephemeral-01

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

# Install additional requirements from SDK
ADD sdk/requirements-${CHANNEL}.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt

# Track to latest AgavePy
# RUN pip install git+https://github.com/TACC/agavepy.git@${AGAVEPY_BRANCH}

CMD ["python", "/reactor.py"]

# Onbuild support
ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN pip install -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
ONBUILD ADD message.json* /message.jsonschema

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
