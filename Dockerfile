FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -yq git python3 python3-pip && \
    apt-get -yq upgrade

# ephemeral working directory
ENV SCRATCH=/mnt/ephemeral-01
WORKDIR ${SCRATCH}
RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}

# add reactor assets from repo
ADD requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt
ADD reactor.py /
ADD config.yml /
ADD context_schemas /
ADD message_schemas /

CMD ["python3", "/reactor.py"]
