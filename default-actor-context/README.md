# Hello World

The `"Hello world"` of Tapis Reactors SDK. This actor prints its name, the message sent to it, and basic diagnostics, such as availability of the TACC HPC [$WORK filesystem](https://portal.tacc.utexas.edu/tutorials/managingio).

## Quick Start

Edit `DOCKER_HUB_ORG` in [`reactor.rc` ](./reactor.rc) to reflect either your DockerHub
username or organization you are authorized to push to. Then build, deploy, and run the reactor using `make` and the [Tapis command line interface (CLI)][1]:
```bash
$ make tests
```

## Build and Deploy

Build and deploy the actor using the [Tapis CLI][1]:
<pre><code>$ tapis actors deploy
Building enho/hello_world:0.1
Finished (1177 msec)
Pushing enho/hello_world:0.1
Finished (2740 msec)
+--------+---------------------------------------------------------------------------------------------------------------------+
| stage  | message                                                                                                             |
+--------+---------------------------------------------------------------------------------------------------------------------+
| build  | Step 1/12 : FROM python:3.6-alpine                                                                                  |
| build  |  ---> 815c1103df84                                                                                                  |
| build  | Step 2/12 : RUN apk update && apk upgrade && apk add git                                                            |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 879c8a0d3695                                                                                                  |
| build  | Step 3/12 : ENV SCRATCH=/mnt/ephemeral-01                                                                           |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> a34c89ec1102                                                                                                  |
| build  | Step 4/12 : WORKDIR ${SCRATCH}                                                                                      |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 5f932eb4c313                                                                                                  |
| build  | Step 5/12 : RUN chmod a+rwx ${SCRATCH} && chmod g+rwxs ${SCRATCH}                                                   |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 8f7badf3462c                                                                                                  |
| build  | Step 6/12 : ADD requirements.txt /tmp/requirements.txt                                                              |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 5fddb46e16fd                                                                                                  |
| build  | Step 7/12 : RUN pip3 install -r /tmp/requirements.txt                                                               |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 5f1f8e1aeb30                                                                                                  |
| build  | Step 8/12 : ADD reactor.py /                                                                                        |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> ed8da8b8c9a1                                                                                                  |
| build  | Step 9/12 : ADD config.yml /                                                                                        |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 89c3bdeee4c2                                                                                                  |
| build  | Step 10/12 : ADD message.json* /message.jsonschema                                                                  |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> fb696161584c                                                                                                  |
| build  | Step 11/12 : RUN pip install ipython requests_futures git+https://github.com/TACC-Cloud/python-reactors.git@develop |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> c07e5eee337d                                                                                                  |
| build  | Step 12/12 : CMD ["python3", "/reactor.py"]                                                                         |
| build  |  ---> Using cache                                                                                                   |
| build  |  ---> 3998e3498978                                                                                                  |
| build  | Successfully built 3998e3498978                                                                                     |
| build  | Successfully tagged enho/hello_world:0.1                                                                            |
| push   | The push refers to repository [docker.io/enho/hello_world]                                                          |
| push   | 0.1: digest: sha256:8c6cbaa13a939f8b12f2241039839f865fb9d56f8978e68837363a9fd1728d59 size: 3245                     |
| create | Created Tapis actor v7Npq8M8MXJNE                                                                                   |
| cache  | Cached actor identifier to disk                                                                                     |
+--------+---------------------------------------------------------------------------------------------------------------------+
</pre></code>

## Running the Actor

View the newly-created actor:
<pre><code>$ tapis actors list
+---------------+--------------+-------+-----------------------+--------------------------+--------+
| id            | name         | owner | image                 | lastUpdateTime           | status |
+---------------+--------------+-------+-----------------------+--------------------------+--------+
| v7Npq8M8MXJNE | hello_world  | eho   | enho/hello_world:0.1  | 2021-03-01T22:22:16.029Z | READY  |
+---------------+--------------+-------+-----------------------+--------------------------+--------+
</pre></code>

Send a message to the actor, returning an execution ID:
<pre><code>$ tapis actors submit -m 'my message' -e MY_ENV_VAR=some_value v7Npq8M8MXJNE
+-------------+---------------+
| Field       | Value         |
+-------------+---------------+
| executionId | ZRgRjy3myQalw |
| msg         | my message    |
+-------------+---------------+
</pre></code>

We can view the status and logs for this execution:
<pre><code>$ tapis actors execs list v7Npq8M8MXJNE
+---------------+----------+
| executionId   | status   |
+---------------+----------+
| ZRgRjy3myQalw | COMPLETE |
+---------------+----------+

$ tapis actors execs logs v7Npq8M8MXJNE ZRgRjy3myQalw
Logs for execution ZRgRjy3myQalw
v7Npq8M8MXJNE INFO Actor received message: my message
v7Npq8M8MXJNE DEBUG This is a DEBUG message from actor v7Npq8M8MXJNE
v7Npq8M8MXJNE INFO This is an INFO message from actor v7Npq8M8MXJNE
v7Npq8M8MXJNE WARNING This is a warning from actor v7Npq8M8MXJNE
v7Npq8M8MXJNE INFO Here's that secret value: secret_value
v7Npq8M8MXJNE INFO Here's that value from the config.yml: not_so_secret
v7Npq8M8MXJNE INFO Using python-reactors version 0.8.0
v7Npq8M8MXJNE DEBUG path '/work/projects' exists
v7Npq8M8MXJNE INFO all checked paths exist
</pre></code>
Since we don't act on the message in `reactor.py` we just see the contents of `STDOUT`.

Alternatively, submit a message and retrieve the logs in one command:
<pre><code>$ tapis actors run -m 'my message' -e MY_ENV_VAR=some_value v7Npq8M8MXJNE
v7Npq8M8MXJNE INFO Actor received message: my message
v7Npq8M8MXJNE DEBUG This is a DEBUG message from actor v7Npq8M8MXJNE
v7Npq8M8MXJNE INFO This is an INFO message from actor v7Npq8M8MXJNE
v7Npq8M8MXJNE WARNING This is a warning from actor v7Npq8M8MXJNE
v7Npq8M8MXJNE INFO Here's that secret value: secret_value
v7Npq8M8MXJNE INFO Here's that value from the config.yml: not_so_secret
v7Npq8M8MXJNE INFO Using python-reactors version 0.8.0
v7Npq8M8MXJNE DEBUG path '/work/projects' exists
v7Npq8M8MXJNE INFO all checked paths exist
</pre></code>

Please see the [Tapis CLI documentation](https://tapis-cli.readthedocs.io/en/latest/usage/actors.html) for details on the most up-to-date CLI.

[1]: https://github.com/TACC-Cloud/tapis-cli
