FROM python:3.7-alpine
RUN apk update && apk upgrade && apk add git

# ephemeral working directory
ENV SCRATCH=/mnt/ephemeral-01
WORKDIR ${SCRATCH}
RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}

# add reactor assets from repo
ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
ADD reactor.py /
ADD config.yml /
ADD context_schemas /
ADD message_schemas /

CMD ["python3", "/reactor.py"]
