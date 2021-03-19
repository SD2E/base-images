FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -yq git python3 python3-pip && \
    apt-get -yq upgrade

# build arguments
ARG SDK_BRANCH=main
ARG TEMPLATE_DIR=cc-tapis-v2-actors
ARG PYTHON=python3

# install Reactors SDK
RUN ${PYTHON} -m pip install git+https://github.com/TACC-Cloud/python-reactors.git@${SDK_BRANCH}

# ephemeral working directory
ENV SCRATCH=/mnt/ephemeral-01
WORKDIR ${SCRATCH}
RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}

# add reactor assets from repo
ADD ${TEMPLATE_DIR}/requirements.txt /tmp/requirements.txt
RUN ${PYTHON} -m pip install --ignore-installed -r /tmp/requirements.txt
ADD ${TEMPLATE_DIR}/reactor.py /
ADD ${TEMPLATE_DIR}/config.yml /
ADD ${TEMPLATE_DIR}/*_schemas /

CMD ["python", "-m", "reactors.cli", "run"]
