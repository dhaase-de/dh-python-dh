Overview
========

Python3 toolbox of Daniel Haase.


Status
------

[![Build Status](https://travis-ci.org/dhaase-de/dh-python-dh.svg?branch=master)](https://travis-ci.org/dhaase-de/dh-python-dh)


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

