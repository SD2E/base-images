FROM ubuntu:20.04
RUN apt-get update && \
    apt-get -yq upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends -yq install \
        tzdata build-essential checkinstall zlib1g libreadline-gplv2-dev \
        libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev \
        libc6-dev libbz2-dev language-pack-en && \
    apt-get -yq install git curl wget vim gcc make

# set locale, preventing python3.6 UnicodeDecodeErrors
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_NUMERIC en_US.UTF-8
ENV LC_TIME en_US.UTF-8
ENV LC_COLLATE en_US.UTF-8
ENV LC_MONETARY en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8
ENV LC_ALL en_US.UTF-8

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
ARG DEFAULT_ACTOR_CONTEXT=/tmp/default_actor_context
ARG BASE_IMAGE_REQUIREMENTS=requirements.txt
ENV AGAVE_CRED_CACHE=/root/.agave

# install Python dependencies, including Reactors SDK
ADD ${BASE_IMAGE_REQUIREMENTS} /tmp/base-image-requirements.txt
RUN python3 -m pip install -r /tmp/base-image-requirements.txt

# ephemeral working directory
ENV SCRATCH=/mnt/ephemeral-01
WORKDIR ${SCRATCH}
RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}

# add default reactor assets via cookiecutter
RUN python3 -m pip install cookiecutter && \
    cd $(dirname "${DEFAULT_ACTOR_CONTEXT}") && \
    python3 -m cookiecutter --no-input -fc main --directory sd2e_base \
		https://github.com/TACC-Cloud/cc-tapis-v2-actors.git \
		name=${DEFAULT_ACTOR_CONTEXT} alias=${DEFAULT_ACTOR_CONTEXT} && \
    cp ${DEFAULT_ACTOR_CONTEXT}/reactor.py / && \
    cp ${DEFAULT_ACTOR_CONTEXT}/config.yml / && \
    cp -r ${DEFAULT_ACTOR_CONTEXT}/*_schemas / && \
    python3 -m pip install --ignore-installed -r \
        ${DEFAULT_ACTOR_CONTEXT}/requirements.txt

# add reactor assets from user's build context
ONBUILD ADD requirements.txt /tmp/requirements.txt
ONBUILD RUN python3 -m pip install --ignore-installed -r /tmp/requirements.txt
ONBUILD ADD reactor.py /
ONBUILD ADD config.yml /
ONBUILD ADD message.json* /message.jsonschema

CMD ["python3", "-m", "reactors.cli", "run"]
