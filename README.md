Overview
========

Python3 toolbox of Daniel Haase.


Status
------

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

0.15.3 (2023-04-19)
-------------------

* increase robustness of processing servers
* simplify release process (version number specification, twine upload)


0.15.2 (2023-02-27)
-------------------

* `prun` now returns a list of all worker process return values


0.15.1 (2023-02-27)
-------------------

* added parallel wrapper `prun`
* added minor logger improvements


0.15.0 (2023-01-08)
-------------------

* updated thirdparty packages `colorama`, `tabulate`, and `tqdm` to fix
  problems with Python 3.10
* removed thirdparty packages `atomicwrites` and `transitions`


0.14.5 (2022-10-28)
-------------------

* extended functionality of `dh.utils.dtstr` (backwards compatible)
* added function `dh.utils.sh`


0.14.4 (2022-03-06)
-------------------

* added function `dh.utils.fmatch1`
* made `dh.utils.Timer` more flexible
* improved `dh.utils.FrequencyEstimator`


0.14.3 (2021-12-14)
-------------------

* log messages can now optionally raise warnings or exceptions
* fixed deprecation warning


0.14.2 (2021-11-16)
-------------------

* servers now use `dh.log.Logger` for info messages, which now also show the current port and can be customized
* added explicit argument 'silent' for loggers to prevent printing on the screen
* added helper functions `sgo` and `igo`


0.14.1 (2020-12-02)
-------------------

* added robust pika wrappers to `dh.network`
* multiple bugfixes
* (version 0.14.0 was not tagged along the way and thus is skipped)


0.13.1 (2018-10-18)
-------------------

* added versions of image processing client/server with updated protocol (JSON-ecoded object is now returned by the server in addition to the actual result)
* added option to display image via IPython in 'dh.image.show'
* updated plot colormaps to map 255 to white


0.13.0 (2018-09-25)
-------------------

* added module 'audio' with very basic functionality
* bugfixes


0.12.1 (2017-10-01)
-------------------

* added config parser using JSON encoding for values
* added wrapper for Tk radio buttons with image support


0.12.0 (2017-08-06)
-------------------

* improved `dh.gui.tk` for Tkinter-based GUIs
* added Ion icon images to data files
* moved colormaps from `dh.image` to `dh.data` module


0.11.3 (2017-06-20)
-------------------

* improved logger
* some smaller improvements


0.11.2 (2017-06-15)
-------------------

* bugfixes


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

* initial version

