Overview
========

dh's Python3 package.

Installation
------------

Run `install.sh` to install the package locally. Other installation
configurations can be achieved directly via `setup.py`.

Documentation
-------------

Run `makeDoc.sh` to build the HTML documentation. The result will be placed
under `doc/build/html/index.html`. Requires Sphinx (Python3, Debian package
`python3-sphinx`) which provides the `sphinx-apidoc` executable.

Testing
-------

Use `runTest.sh` to run all unit tests (including tests in the documentation).
Requires `nose` for Python3 (Debian package `python3-nose`), which provides the
`nosetests3` executable.

ToDo (framework)
----------------

* use `virtualenv` when installing the package to create the documentation
* use `nose2` instead of `nose` for testing
* include README.txt etc. into package

ToDo (new content)
------------------

* interactive image pipeline viewer
* progress bar

