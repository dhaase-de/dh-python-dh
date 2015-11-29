#!/usr/bin/python3

import os
import os.path
import re

try:
    # setuptools has wheel support (command "bdist_wheel"), but is not in the standard library
    import setuptools
    setup = setuptools.setup
except ImportError:
    # fallback option without wheel support
    import distutils.core
    setup = distutils.core.setup

##
## preparations
##

# (relative) directories of the top-level packages
packageDirBase = "dh"
packageDirThirdparty = os.path.join(packageDirBase, "thirdparty")

# parse version from package's init file
version = None
versionFilename = os.path.join(packageDirBase, "__init__.py")
with open(versionFilename, "r") as f:
    for line in f:
        versionMatch = re.search("^\s*__version__\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+(-dev)?)\"", line)
        if versionMatch is not None:
            version = versionMatch.group(1)
            break
if version is None:
    raise RuntimeError("Could not parse version from file '{}'".format(versionFilename))

# prepare package list (list is: base package plus "thirdparty" module plus one package for each third party module)
packages = [packageDirBase, packageDirThirdparty]
for (path, packageSubdirsThirdparty, _) in os.walk(packageDirThirdparty):
    for packageSubdirThirdparty in packageSubdirsThirdparty:
        if re.search("^[^_]", packageSubdirThirdparty):
            packages.append(os.path.join(path, packageSubdirThirdparty))

##
## main call
##

setup(
    name=packageDirBase,
    version=version,
    description="Personal package of Daniel Haase",
    author="Daniel Haase",
    packages=packages,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)

