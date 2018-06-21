# Base Images

[![Build Status](https://travis-ci.org/SD2E/base-images.svg?branch=master)](https://travis-ci.org/SD2E/base-images)

This repository supports development, maintenance, and extension of the base
images used by the SD2 program to sharing code and capabilities. A matrix of
Linux distributions and high-level languages is supported efficiently by
this arrangement.

## Images Catalog

|                base                |                     languages                    |                apps               |                         reactors                         |
|:----------------------------------:|:------------------------------------------------:|:---------------------------------:|:--------------------------------------------------------:|
| alpine36 centos7 miniconda3 ubuntu16 ubuntu17 | ubuntu16/python2 ubuntu17/python3 ubuntu17/java8 | python2/ubuntu16 python3/ubuntu17 | python2/ubuntu16 python2-conda/ubuntu16 python3/ubuntu17 |

## Architecture

Images are layered hierarchically to promote layer caching and help ensure
that essential configurations and computational assets get propagated
to developers and researchers relying on them.

```
+-------------+
|             |
| <os>:dist   |
|             |
+-------------+
     |||
+-------------------------+    +----------------------+
|                         |    |                      |
| sd2e/base:<dist>(-edge) |....| sd2e/jupyterhub-user |
|                         |    |                      |
+-------------------------+    +----------------------+
           |
+---------------------------+  +-------------------------+
|                           |  |                         |
| sd2e/<lang>:<dist>(-edge) |--| sd2e/apps:<lang>(-edge) |
|                           |  |                         |
+---------------------------+  +-------------------------+
           |
+-----------------------------+
|                             |
| sd2e/reactors:<lang>(-edge) |
|                             |
+-----------------------------+
```

## Container image types

Four image types are currently supported:

* base : foundation layer for other images
* language : images configured to support development in a specific language
* apps : extension of the language environment supporting Agave apps
* reactors : extension of the language environment supporting Reactors

Coming soon:
* jupyterhub-user : shared infrastructure for container and HPC Jupyter

### Documentation

* [base](base/README.md)
* [languages](languages/README.md)
* [reactors](reactors/README.md)
* [apps](apps/README.md)

## Building

Requirements:
* Make 3.81+ and Bash 3.2.57+
* Docker CE/EE 17.05+ & plenty of HDD space free for use by Docker
* An account on the public Docker Cloud registry

Development is Makefile-driven, with parameterization via build variables.

```
| Targets                  | Command                      | Options                                   | Variables                   |
|--------------------------|------------------------------|-------------------------------------------|-----------------------------|
| build/push all images    | make all                     |                                           |                             |
| build all images         | make builds                  |                                           |                             |
| specific image type      | make <type>(-build)          | apps, base, jupyter,  languages, reactors |                             |
| specific release channel | make <target>-(build)        | stable, edge                              | CHANNEL=<channel>           |
| specific base            | make base-(build)            | ubuntu16, ubuntu17, miniconda3, ubuntu18  | BASE=<dist>                 |
| specific language        | make language-(build)        | python2, python3                          | LANGUAGE=<lang>             |
| specific language + base | make [apps,reactors]-(build) | see above                                 | LANGUAGE=<lang> BASE=<dist> |
```

For example, the following command builds, but doesn't push, the `python2`
language image based on `ubuntu16` using `Dockerfile-edge`.

```shell
make languages-build LANGUAGE=python2 BASE=ubuntu16 CHANNEL=edge
```

### Special variables

Values passed to these variables inform the build process:

* `AGAVEPY_BRANCH` - AgavePy code branch [develop]
* `PYTHON_PIP_VERSION` - Version of pip installed in Python images [9.0.3]
* `NO_CACHE` - Rebuild everything without the Docker cache. [0]
* `NO_REMOVE` - Don't remove intermediate containers (helpful for debugging). [0]
* `CHANNEL` - Default is [stable]. Repositories explicitly also support `edge`
* `DOCKER_PULL` - Set `DOCKER_PULL=1` to force pull on build. [0]

Example: Build Python2 based on Pip 9.0.1 and don't remove intermediates.

```shell
make languages-build LANGUAGE=python2 PYTHON_PIP_VERSION=9.0.1 NO_REMOVE=1
```

## Testing

Formal testing is not fully implemented, though container builds are conducted
automatically via TravisCI on push to any branch. Images are pushed automatically
to the SD2E DockerHub registry on successful commits to `master`.

