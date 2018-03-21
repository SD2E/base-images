FROM sd2e/java8:ubuntu17

ARG LANGUAGE=java8
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

# # Core Python3 requirements
# ADD requirements-py3.txt /tmp/requirements.txt
# RUN pip3 install -r /tmp/requirements.txt
# RUN pip3 install --upgrade git+https://github.com/TACC/agavepy.git@${AGAVEPY_BRANCH}

# In-progress language libraries

# ADD reactors /reactors
# ADD agaveutils /agaveutils

# Default actor and config files
#ADD reactor.py /
ADD config.yml /
CMD ["java"]

# Onbuild support
#ONBUILD ADD requirements.txt /tmp/requirements.txt
#ONBUILD RUN pip3 install -r /tmp/requirements.txt
#ONBUILD ADD reactor.java /
ONBUILD ADD config.yml /

# Close out making absolutely sure that work directory is set
WORKDIR ${SCRATCH}
