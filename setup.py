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


# read version number from text file
version_filename = os.path.join(sourceDir, "__init__.py")
with open(version_filename, "r") as f:
    for line in f:
        match = re.match(r"__version__\s*=\s*['\"]([a-zA-Z0-9-_.]+)['\"]", line)
        if match is not None:
            version = match.group(1)
            break
    else:
        # end of file, version was not found
        raise RuntimeError("Could not parse version number from file '{}'".format(version_filename))


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
    url="https://github.com/dhaase-de/dh-python-dh",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    packages=packages,
    package_data={packageName: [
        "data/colormaps/*.json",
        "data/icons/ionicons/png/512/*.png",
        "data/images/*.npy",
        "data/images/*.npz",
    ]},
    scripts=["bin/raspiCameraClient.py", "bin/raspiCameraServer.py"],
)
