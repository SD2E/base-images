# Base Images

[![Docker publish](https://github.com/SD2E/base-images/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/SD2E/base-images/actions/workflows/docker-publish.yml)

This repository supports development, maintenance, and extension of the base
images used by the SD2 program to sharing code and capabilities.

## Images Catalog

|   base   |      reactors      |
|:--------:|:------------------:|
| ubuntu20 |  reactors:python3  |

## Building

Requirements:
* Make 3.81+ and Bash 3.2.57+
* Docker CE/EE 17.05+ & plenty of HDD space free for use by Docker
* An account on the public Docker Cloud registry

Change the `DOCKER_ORG` variable in [config.mk](config.mk) to a Dockerhub organization to which you have push access. If necessary, also change the `AGAVE_CRED_CACHE` variable to the location of your Agave/Tapis credentials cache (in case your cache is set to a non-default location). Development is Makefile-driven, with parameterization via build variables.

|                  Targets                  | Command |
|:-----------------------------------------:|:-------:|
| build the base image (`reactors:python3`) |  image  |
|        run the base image locally         |  tests  |

## Testing

Work in progress.
