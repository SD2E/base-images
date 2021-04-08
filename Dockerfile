FROM ubuntu:20.04
RUN apt-get update && \
    apt-get -yq upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends -yq install \
        tzdata build-essential checkinstall zlib1g libreadline-gplv2-dev \
        libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev \
        libc6-dev libbz2-dev && \
    # TODO: remove
    # Quality of life config
    apt-get -yq install git curl wget vim zsh gcc make ripgrep && \
    chsh -s $(which zsh) && \
    echo 'bindkey -v' > ~/.zshrc

# python build args
ARG PYTHON_VERSION=3.6.3
ARG PYTHON_TARBALL=https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
ARG PYTHON_STUB=Python-${PYTHON_VERSION}

# Install pinned Python version
WORKDIR /tmp
RUN wget ${PYTHON_TARBALL} -O ${PYTHON_STUB}.tgz && \
    mkdir ${PYTHON_STUB} && \
    tar -xzf ${PYTHON_STUB}.tgz -C ${PYTHON_STUB} --strip-components 1 && \
    cd ${PYTHON_STUB} && \
    ./configure --enable-optimizations && \
    make install && make clean && \
    python3 -m pip install --upgrade pip

# build arguments
ARG SDK_BRANCH=main
ARG TEMPLATE_DIR=cc-tapis-v2-actors
ARG PYTHON=python3
ARG BASE_IMAGE_REQUIREMENTS=requirements.txt
ENV AGAVE_CRED_CACHE=/root/.agave

# install Python dependencies, including Reactors SDK
ADD ${BASE_IMAGE_REQUIREMENTS} /tmp/base-image-requirements.txt
RUN ${PYTHON} -m pip install -r /tmp/base-image-requirements.txt

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
