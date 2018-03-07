# Reactor Base

This is not the objective for an elite strike force of Space 
Marines who need to disable the planetary shields so that
the invasion can begin. Instead, it is the source repository
for the Python2 base image for TACC Reactors. 

You do not need to build it yourself, as it is available in
TACC's Docker Cloud Registry.

Stable: `taccreactors/reactor-python2:stable`
Pre-release: `taccreactors/reactor-python2:testing`
Experimental: `taccreactors/reactor-python2:edge`

## Libraries

This image provides helpful utlity libraries and utilities
for you to use in your Python-based Reactors. It is likely
that more basic functionality will be added to this image 
in the future, but we will try hard to maintain full backward
compatibility. Also, you should be aware that anything 
these libaries do can be accomplished manually. We are simply
trying to reduce the amount of boilerplate needed to deploy
functions-as-a-service at TACC.

Presently, the following community-maintained modules are
installed in the base image:
* [agavepy][1]
* [jmespath][3]
* [jsonschema][4]
* [PyYAML][5]

There is also a custom module called [config][2] that 
provides drop-dead simple file-based configuration capability
for your Reactors.  

## ONBUILD

Because Reactors are based on Docker container images, we are able
to take advantage of many features of the Docker ecosystem. Specifically,
we use ONBUILD support in this base image. When you deploy a Reactor
derived `FROM taccreactors/python2` it will do the following:

1. Copy in `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Copy in `reactor.py`
4. Copy in `config.yml`
5. Copy in `message.json` 
6. Set the default command for the image to `python reactor.py`

Furthemore, in the Reactor runtime hosted in the TACC Cloud, your
Reactors will automatically be configured with an active Agave API 
client owned by your TACC identity. 

[1]: agave
[2]: config
[3]: jmespath.py
[4]: jsonschema
[5]: PyYAML
