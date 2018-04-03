# Changelog

All signficiant changes to the `reactors:python2` image will be recorded here.

## 0.6.0 - New base image.
Added
* Test coverage via pytest and flake8

Changed
* Rationalize use of reactors library
* Parameterizable logger - choice of log file and level
* Logger now prints actorID and executionID automatically
* Agaveutils is now a submodule since a lot of it is Abaco- or SD2 specific
* Verified all source files should be Python3 compatible
* All source files pass stringent flake8 validation

Removed
* Reference to hand-coded config.py. Replaced with tacconfig library.

## 0.5.0 First Release
