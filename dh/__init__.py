"""
Personal Python package of Daniel Haase.
"""

from os.path import abspath, dirname, join
from warnings import warn


# read version number from text file
try:
    _versionFilename = join(dirname(abspath(__file__)), "VERSION.txt")
    with open(_versionFilename, "r") as _f:
        for line in _f:
            line = line.strip()
            if (line == "") or (line[0] == "#"):
                # ignore empty lines and comments
                continue
            else:
                # the first valid line will be used as version number
                __version__ = line
                break
        else:
            # end of file, version was not found
            warn("Found no valid version number in file '{}'".format(_versionFilename))
            __version__ = "unknown"
except Exception as e:
    warn("Failed to get version number from file '{}' (error: '{}')".format(_versionFilename, e))
    __version__ = "unknown"
finally:
    # purge
    del abspath
    del dirname
    del join
    del warn
    del _versionFilename
    try:
        del _f
    except NameError:
        pass
