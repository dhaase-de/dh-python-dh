#!/usr/bin/python3

import os.path
import re

from distutils.core import setup

##
## preparations
##

# name of the top-level package - must match top level directory name
packageName = "dh"

# parse version from package's init file
version = None
versionFilename = os.path.join(packageName, "__init__.py")
print(versionFilename)
with open(versionFilename, "r") as f:
    for line in f:
        versionMatch = re.search("^\s*__version__\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+)\"", line)
        if versionMatch is not None:
            version = versionMatch.group(1)
            break
if version is None:
    raise RuntimeError("Could not parse version from file '{}'".format(versionFilename))

##
## main call
##

setup(
    name = packageName,
    version = version,
    description = "Personal package of Daniel Haase",
    author = "Daniel Haase",
    packages = [packageName],
)

