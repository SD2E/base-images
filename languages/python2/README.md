# Languages:Python2

Base images tailored to building Python2-based containers. Language images
are available and supported for alpine36, ubuntu16, ubuntu17 operating system
bases. Older versions (ubuntu14) and pre-release versions (ubuntu18) are
available but not yet officially supported. All language images have a stable
and `-edge` release channel.

The Python2 Apps and Reactors images are built using the 'ubuntu17' tag.

## Dependency management

Dependency management is via pip. The image also supports `virtualenv`.

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

### Special

One can pass a value for these variables and they'll inform the build process.

`AGAVEPY_BRANCH` - Default is currently `develop`
`PYTHON_PIP_VERSION` - Default is currently `9.0.3`
`NO_CACHE` - Rebuild everything without the Docker cache. Default is unset.
`CHANNEL` - Default is `stable`. Repositories are configured to explicitly also support `edge`

### Additional files

One can parameterize `RUN`, `ADD`, and other Dockerfile commands using
build-time arguments. This is used specifically in the Python images to
support a stable and edge `requirements.txt` file
