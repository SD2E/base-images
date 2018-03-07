FROM abacosamples/base-ubu:dev

ENV _REACTORS_VERSION=0.5.0

ARG LANGUAGE=python2
ARG VERSION=0.5.5
ARG AGAVEPY_BRANCH=develop

# Discoverable version inside the container
RUN echo -e "TACC.cloud Reactors\nLanguage:${LANGUAGE}\nVersion:${VERSION}" > /etc/reactors-VERSION

# Essential requirements
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD reactors /reactors

ADD reactor.py /
ADD config.yml /
CMD ["python", "/reactor.py"]

# This is a container-local directory
# that all UIDs can write to. It will
# of course, not survive when
# the container is torn down.
# 
# Other entries in /mnt/ will
# be various types of persistent
# storage

RUN mkdir -p /mnt/ephemeral-01 && \
    chmod a+rwx /mnt/ephemeral-01 && \
    chmod g+rwxs /mnt/ephemeral-01

ENV _PROJ_CORRAL=
ENV _PROJ_STOCKYARD=
ENV _USER_WORK=
ENV _REACTOR_TEMP=/mnt/ephemeral-01

WORKDIR /mnt/ephemeral-01

ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN pip install -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
