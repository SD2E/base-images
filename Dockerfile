FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -yq git python3 python3-pip && \
    apt-get -yq upgrade

# build arguments
ARG SDK_BRANCH=main
ARG TEMPLATE_DIR=cc-tapis-v2-actors
ARG PYTHON=python3
ENV AGAVE_CRED_CACHE=/root/.agave

# install Reactors SDK
RUN ${PYTHON} -m pip install git+https://github.com/TACC-Cloud/python-reactors.git@${SDK_BRANCH}

# ephemeral working directory
ENV SCRATCH=/mnt/ephemeral-01
WORKDIR ${SCRATCH}
RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}

# add default reactor assets
ADD ${TEMPLATE_DIR}/requirements.txt /tmp/requirements.txt
RUN ${PYTHON} -m pip install --ignore-installed -r /tmp/requirements.txt
ADD ${TEMPLATE_DIR}/reactor.py /
ADD ${TEMPLATE_DIR}/config.yml /
ADD ${TEMPLATE_DIR}/*_schemas /

# add reactor assets from user's build context
ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN ${PYTHON} -m pip install --ignore-installed -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
ONBUILD ADD *_schemas /

CMD ["python3", "-m", "reactors.cli", "run"]
