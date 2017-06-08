Overview
========

Python3 toolbox of Daniel Haase.


Status
------

[![Build Status](https://travis-ci.org/dhaase-de/dh-python-dh.svg?branch=master)](https://travis-ci.org/dhaase-de/dh-python-dh)
[![License](https://img.shields.io/github/license/dhaase-de/dh-python-dh.svg)](LICENSE.txt)


Installation
------------

Run `scripts/build-install-dev.sh` to install the package. See the `scripts`
dir for further options.


Documentation
-------------

Run `scripts/build-doc.sh` to build the HTML documentation. The result will be
placed under `doc/build/html/index.html`. Requires Sphinx (Python3, Debian
package `python3-sphinx`) which provides the `sphinx-apidoc` executable.


Testing
-------

Use `scripts/check-tests.sh` to run all unit tests (including tests in the
documentation). Requires `nose` for Python3 (Debian package `python3-nose`),
which provides the `nosetests3` executable.


Changelog
=========

0.11.1 (2017-06-09)
-------------------

* several smaller improvements
* purged framework


0.11.0 (2017-06-06)
-------------------

* added `colorama`, `humanize`, `transitions` to thirdparty modules
* updated thirdparty modules to their most recent stable versions
* added module `dh.log`
* created examples dir


0.10.1 (2017-05-23)
-------------------

* slightly purged framework
* removed accidental debug output


0.10.0 (2017-05-23)
-------------------

* added module `dh.hardware.raspi`, containing client/server functionality for
  the Raspberry Pi camera
* refactored `dh.network`
* moved `dh.utils.ejson` to own module `dh.ejson`


0.9.0 (2017-03-08)
------------------

* added Travis CI support (which includes: Travis CI config file, requirements
  file, more tests, fixes for version-related bugs, changing version numbering
  scheme)
* some smaller bugfixes and improvements


0.8.1 (2017-02-21)
------------------

* improved `dh.network`: added `ImageProcessingServer` and client, added
  `NumpySocketMessage`, and improved the general performance (latency dropped
  from ~250ms to ~4ms for a no-op image processing client-server communication
  on the same machine)
* smaller improvements


0.8.0 (2017-02-19)
------------------

* added module `dh.network` and functionality to send various high-level
  message types via sockets (plus example)
* added extended JSON encoder/decoder to `dh.utils`


0.7.0 (2017-02-19)
------------------

* added module `dh.plot`, containing wrapper classes for Google charts
* smaller improvements and bugfixes


0.6.0 (2017-01-27)
------------------

* note: version numbers 0.4.x and 0.5.x are skipped due to the amount of
  changes since 0.3.0
* *vastly* improved `dh.utils` and `dh.image` (added a lot of new functionality
  and bugfixes)
* added `dh.data` module
* integrated multiple thirdparty modules `tabulate`, `tqdm`
* updated framework (scripts, license)


0.3.0 (2015-11-29)
------------------

* improved framework (documentation, unit tests, dev dir, scripts, ...)
* extended `dh.utils`


0.2.0 (2015-08-31)
------------------

* first version

