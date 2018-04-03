# Languages:Python2

Operating System: Language-specific images are based on sd2e/base:<os>

## Dependency management

Dependency management is via pip > 9.0.1. The image also supports `virtualenv`.

## Docker specifics

### Dockerfiles

Dockerfiles follow the naming convention: `Dockerfile.<os>(-channel)`. If
`channel` is ommitted, the Dockerfile is assumed to provide instructions
for the `stable` channel. If an appropriately-named Dockerfile can't be
found for a channel-specific build, the `stable` channel is used.

### Variables

`BASE`, `LANGUAGE` and `CHANNEL` are inherited from the build environment. In
addition, `NO_CACHE` can be set to cause the build system to ignore the Docker
cache when building.

`BASE`, `LANGUAGE` and `CHANNEL` are passed into `docker build` as build-time
arguments, as all `base-images` Dockerfiles contain these as `ARG` entries.

### Additional files

One can parameterize `RUN`, `ADD`, and other Dockerfile commands using
build-time arguments. This is used specifically in the Python images to
support a stable and edge `requirements.txt` file

