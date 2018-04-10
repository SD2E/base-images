# Base

Docker images upon which language-specific apps and reactors base images
are built. Presently alpine36, ubuntu16, centos7, and ubuntu17 are supported.
Older versions (ubuntu14) and pre-release versions (ubuntu18, miniconda3) are available
but not officially supported. All base images have a stable
and `-edge` release channel.

Dockerhub:
* `sd2e/base:<os>`
    * `alpine36`
    * `centos7` (preferred)
    * `ubuntu14` (deprecated)
    * `ubuntu16`
    * `ubuntu17` (preferred)
    * `ubuntu18` (experimental)
    * `miniconda3` (experimental)

## Features

These are vanilla operating system images with the following exceptions:

1. A handful of extras are guaranteed to be installed so as to minimize frustration in container development
    1. vim, git, curl, rsync, jq, and bash
2. Shadow mount points are created at the root level of the container filesystem to enable transparent compatibility with TACC's HPC containers implementation. Environment variables are set for project- and user-level storage and archival resources.

[Home](../README.md) | [Languages](../languages/README.md) | [Apps](../apps/README.md) | | [Reactors](../reactors/README.md)
