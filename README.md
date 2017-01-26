Overview
========

Python3 toolbox of Daniel Haase.


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


0.3.0 (2015-11-29)
------------------

* improved framework (documentation, unit tests, dev dir, scripts, ...)
* extended `utils`


0.2.0 (2015-08-31)
------------------

* first version

