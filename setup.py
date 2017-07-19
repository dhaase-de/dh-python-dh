import os
import os.path


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
try:
    versionFilename = os.path.join(sourceDir, "VERSION.txt")
    with open(versionFilename, "r") as f:
        for line in f:
            line = line.strip()
            if (line == "") or (line[0] == "#"):
                # ignore empty lines and comments
                continue
            else:
                # the first valid line will be used as version number
                version = line
                break
        else:
            # end of file, version was not found
            raise RuntimeError("Found no valid version number in file '{}' - run 'scripts/version-setFromGit.sh' first or use the build scripts to build/install this package".format(versionFilename))
except Exception as e:
    raise RuntimeError("Failed to get version number from file '{}' (error: '{}') - run 'scripts/version-setFromGit.sh' first or use the build scripts to build/install this package".format(versionFilename, e))


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
        "VERSION.txt",
        "data/*.npy",
        "data/*.npz",
        "data/icons/ionicons/png/512/*.png",
        "image/colormaps/*.json",
    ]},
    scripts=["bin/raspiCameraClient.py", "bin/raspiCameraServer.py"],
)
