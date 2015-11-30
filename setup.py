#!/usr/bin/python3

import os
import os.path
import re

try:
    # setuptools has wheel support (command "bdist_wheel"), but is not in the standard library
    import setuptools
    print("==> using module 'setuptools'")
    setup = setuptools.setup
except ImportError:
    # fallback option without wheel support
    import distutils.core
    print("==> module 'setuptools' not found, falling back to 'distutils'")
    setup = distutils.core.setup

##
## preparations
##

# package dirs
packageName = "dh"
packageDir = os.path.abspath(os.path.dirname(__file__))
sourceDir = os.path.join(packageDir, packageName)

# parse version from package's main file
version = None
versionFilename = os.path.join(sourceDir, "__init__.py")
with open(versionFilename, "r") as f:
    for line in f:
        versionMatch = re.search("^\s*__version__\s*=\s*\"([0-9]+\.[0-9]+\.[0-9]+(-dev)?)\"", line)
        if versionMatch is not None:
            version = versionMatch.group(1)
            break
if version is None:
    raise RuntimeError("Could not parse version from file '{}'".format(versionFilename))

# prepare package list (any directory under the source dir which contains an '__init__.py' file)
packages = []
for (absDir, _, filenames) in os.walk(sourceDir):
    if "__init__.py" in filenames:
        packages.append(os.path.relpath(absDir, packageDir))

##
## main call
##

setup(
    name=packageName,
    version=version,
    description="Personal Python package of Daniel Haase",
    author="Daniel Haase",
    packages=packages,
    package_data={packageName: ["data/lena.npy"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
