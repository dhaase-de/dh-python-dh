"""
Provides/handles example data (e.g., images, text files, etc.).
"""

import os.path

# path into which setup.py installs all data files
_DATA_DIR = os.path.abspath(os.path.dirname(__file__))


##
## helpers
##


def _loadNpy(basename):
    import numpy as np
    return np.load(os.path.join(_DATA_DIR, basename))


def _loadNpz(basename):
    import numpy as np
    X = np.load(os.path.join(_DATA_DIR, basename))
    return X[X.keys()[0]]


##
## general data
##


def M(rows=3, columns=4):
    """
    Simple NumPy test matrix.

    The returned matrix is of size `rows`x`columns` and contains the integers
    from 0 to (`rows` * `columns` - 1).
    """

    import numpy as np

    return np.array(range(rows * columns)).reshape((rows, columns))


##
## image data
##


def lena():
    """
    The famous Lena image, widely used in image processing.

    Source: The USC-SIPI Image Database (http://sipi.usc.edu/database/).
    """

    return _loadNpz("lena.npz")


def pal():
    """
    PAL image (Philips PM5544 test card).

    Source:
    https://commons.wikimedia.org/wiki/File:PM5544_with_non-PAL_signals.png.
    The image is released into the public domain.
    """

    return _loadNpz("pal.npz")
