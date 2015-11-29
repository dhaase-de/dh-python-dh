"""
Provides/handles example data (e.g., images, text files, etc.).
"""

import os.path

# path into which setup.py installs all data files
_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")


def _loadNpy(basename):
    import numpy as np
    return np.load(os.path.join(_DATA_DIR, basename))


def lena():
    """
    The famous Lena image, widely used in image processing.
    """

    return _loadNpy("lena.npy")
