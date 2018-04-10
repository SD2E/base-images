FROM sd2e/python3:ubuntu17-edge

ARG CHANNEL=edge
ARG LANGUAGE=python3
ARG VERSION=0.5.5
ARG AGAVEPY_BRANCH=develop
ARG SCRATCH=/mnt/ephemeral-01

# Discoverable version inside the container
RUN echo "TACC.cloud Reactors\nLanguage: ${LANGUAGE}\nVersion: ${VERSION}" > /etc/reactors-VERSION
# Helpful env variable
ENV REACTORS_VERSION=${VERSION}

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

# Core Python3 requirements
ADD requirements-${LANGUAGE}.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
RUN pip3 install --upgrade git+https://github.com/TACC/agavepy.git@${AGAVEPY_BRANCH}

# In-progress language libraries

ADD reactors /reactors
# ADD agaveutils /agaveutils

# Default actor and config files
ADD reactor.py /
ADD config.yml /
ADD abacoschemas /abacoschemas
ADD message.json* /message.jsonschema

CMD ["python3", "/reactor.py"]

# Onbuild support
ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN pip3 install --upgrade -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
# Allow for message.json and message.jsonschema as both are valid extensions
ONBUILD ADD message.json* /message.jsonschema

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
