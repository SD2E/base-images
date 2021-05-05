# SD2E Base Images

[![Docker publish](https://github.com/SD2E/base-images/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/SD2E/base-images/actions/workflows/docker-publish.yml)

This repository supports development, maintenance, and extension of the Docker base
images used by the SD2 program for sharing code. In particular, this repository maintains the [`sd2e/reactors:python3`][3] base image.

## Basic Usage

The `sd2e/reactors:python3` base image is regularly pushed to [DockerHub][3]. One can pull the image using the [Docker CLI][4]:
```bash
docker pull sd2e/reactors:python3
```
...or use it as a base image in a Dockerfile for a custom [Tapis Actor/Reactor][5]:
```Dockerfile
FROM sd2e/reactors:python3
RUN pip install -r my_requirements.txt
# ...
```
Please see the [Tapis Reactors SDK][6] for more details on how to develop and deploy custom Actors.

## Building and Testing

### Using Docker CLI

```bash
docker build -t sd2e/reactors:python3 .
docker run --rm -v $HOME/.agave:/root/.agave sd2e/reactors:python3 --help
```

### Using make

- Change the `DOCKER_ORG` variable in [config.mk](config.mk) to a Dockerhub organization to which you have push access. 
- If you have not already, install the [Tapis CLI][1] and log in using your Agave/Tapis credentials
    - If necessary, also change the value of the [`AGAVE_CRED_CACHE`](config.mk) variable to the location of your Agave/Tapis credentials cache (in case your cache somewhere other than the default `$HOME/.agave`). 
- Run tests in a Docker container: `make tests`

### Using act

The [Docker publish Action](./.github/workflows/docker-publish.yml) builds, tests, and pushes the `reactors:python3` base image. You can run these tests locally using the [act CLI][2]. Note that passwords for DockerHub and Tapis should be passed as `--secret`s, while other options such as DockerHub organization should be passed as `--env`s.
```bash
act --secret TAPIS_PASSWORD='my_tapis_password' --env TAPIS_USER='my_tapis_username' pull_request
```

To additionally push the Docker image, pass the `push` event with Docker credentials as arguments. Note that this requires push permissions for the specified `DOCKER_USER` and `DOCKER_ORG`.
```bash
act --secret TAPIS_PASSWORD='my_tapis_password' --secret DOCKER_PASSWORD='my_dockerhub_password' \
    --env DOCKER_USER='my_dockerhub_username' --env DOCKER_ORG='my_dockerhub_organization' \
    --env TAPIS_USER='my_tapis_username' push
```

Please see the [act documentation][2] for details.

[1]: https://tapis-cli.readthedocs.io/en/latest/
[2]: https://github.com/nektos/act
[3]: https://hub.docker.com/r/sd2e/reactors
[4]: https://www.docker.com/
[5]: https://tapis-cli.readthedocs.io/en/latest/usage/actors.html
[6]: https://github.com/TACC-Cloud/python-reactors
