"""
Provides/handles example data (e.g., images, text files, etc.).
"""

import os.path

# path into which setup.py installs all data files
_DATA_DIR = os.path.abspath(os.path.dirname(__file__))


def _loadNpy(basename):
    import numpy as np
    return np.load(os.path.join(_DATA_DIR, basename))


def lena():
    """
    The famous Lena image, widely used in image processing.
    """

    return _loadNpy("lena.npy")


def M(rows=3, columns=4):
    """
    Simple NumPy test matrix.

    The returned matrix is of size `rows`x`columns` and contains the integers
    from 0 to (`rows` * `columns` - 1).
    """

    import numpy as np

    return np.array(range(rows * columns)).reshape((rows, columns))
