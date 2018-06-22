# Feature Roadmap

# 0.1.0 Dec 22 2017

* ONBUILD triggers
    * requirements.txt for pip
    * config.yml for configuring via Python dict
    * reactor.py as default entrypoint name
* Environment variables pointing to project-level native filesystem mounts
* Support for running as TACC uid/gid
* Debut of tacc_cloud_utils Python library
    * JMES-path based filtering of JSON structs and Python dicts
    * Methods for working with Agave-canonical URLs

# 0.2.0 Jan 15 2017

* Python3 support
* Access to user-specific WORK storage inside Reactors
* Improvements to tacc_cloud_utils
    * New persistent key-value store based on Agave's metadata service
    * Synchronous upload/download support
    * Arbitrary child processes via Python subprocess()
    * Support for policy-based permissions grants
