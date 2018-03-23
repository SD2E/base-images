# Base Images

[![Build Status](https://travis-ci.org/SD2E/base-images.svg?branch=master)](https://travis-ci.org/SD2E/base-images)

This repository supports development, maintenance, and extension of the base
images used by the SD2 program to sharing code and capabilities. A matrix of
Linux distributions and high-level languages is supported efficiently by
this arrangement.

## Architecture

Images are layered hierarchically to promote layer caching and help ensure
that essential configurations and computational assets get propagated
to developers and researchers relying on them.

```
+-------------+
|             |
| ubuntu:dist |
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
| sd2e/<lang>:<dist>(-edge) |..| sd2e/apps:<lang>(-edge) |
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

There are three classes of image currently supported:

* base : foundation layer for other images
* language : images configured to support development in a specific language
* reactors : extension of the language environment supporting Reactors

Two more are coming soon:
* jupyterhub-user : shared infrastructure for container and HPC Jupyter
* apps : extension of the language environment supporting Agave apps

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
| specific base            | make base-(build)            | ubuntu16, ubuntu17                        | BASE=<dist>                 |
| specific language        | make language-(build)        | python2, python3                          | LANGUAGE=<lang>             |
| specific language + base | make [apps,reactors]-(build) | see above                                 | LANGUAGE=<lang> BASE=<dist> |
```

You can also set `NO_CACHE=1` to force a completely fresh build.

For example, the following command builds, but doesn't push, the `python2`
language image based on `ubuntu16` using `Dockerfile-edge`.

```shell
make languages-build LANGUAGE=python2 BASE=ubuntu16 CHANNEL=edge
```

## Testing

Formal testing is not yet implemented, though container builds are conducted
automatically via TravisCI on push to any branch. Images are pushed automatically
to the SD2E DockerHub registry on successful commits to `master`.

