# Reactors::Python2

A base image for building Python2-based [Abaco][1] Reactors.

* [DockerHub][]
    * Stable: `sd2e/reactors:python2`
    * Pre-release: `sd2e/reactors:python2-edge`

## Features

### TACC.cloud API Integration

When deployed, a Reactor is automatically configured with valid user-specific
credentials for using TACC.cloud APIs. These currently include the Agave and
Abaco APIs, but will soon also include TACC's hosted GitLab,
Continuous Integration, and Container Registry services.

### Filesystems

Abaco-deployed containers are deployed read-only, but have a few options to write data:

1. The `/mnt/ephemeral-01`, which is the default container working directory, is writable but is temporary to the current execution
2. Project storage is accessible via the path defined by `_PROJ_STOCKYARD`
3. Project archival storage is accessible via the path defined by `_PROJ_CORRAL`

### ONBUILD support

When an image is built using this image, either manually or as part of the
`abaco deploy` workflow, it will automatically do the following via [ONBUILD][3]:

1. Copy in `requirements.txt`
2. Run `pip install --upgrade -r requirements.txt`
3. Copy in `reactor.py`, `config.yml`, and `message.jsonschema` to the container root directory
4. Set the default command to `python reactor.py`

### Python libraries

In addition those Python modules supplied by its source image
[sd2e/python2:ubuntu17][4], this image features the `reactors` utility module
to help reduce the boilerplate of working with TACC.cloud APIs and performing
other routine tasks.

* [agavepy][5]
* [agavedb][6]
* [taccconfig][7]
* [jmespath][8]
* [jsonschema][9]

[1]: https://useabaco.cloud/
[2]: https://cloud.docker.com/swarm/sd2e/repository/docker/sd2e/reactors/
[3]: https://docs.docker.com/engine/reference/builder/#onbuild
[4]: TBD
[5]: https://pypi.python.org/pypi/agavepy/
[6]: https://pypi.python.org/pypi/agavedb/
[7]: https://pypi.python.org/pypi/tacconfig/
[8]: https://pypi.python.org/pypi/jmespath/
[9]: https://pypi.python.org/pypi/jsonschema/
