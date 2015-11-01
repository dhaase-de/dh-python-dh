"""
Functions for scientific applications.
"""

#import numpy as np

import dh.utils


def tir(*args):
    """
    The items of `*args` are flattened (via :func:`dh.utils.flatten`), rounded,
    converted to `int` and combined into a tuple.

    The primary use-case of this function is to pass point coordinates to
    certain OpenCV functions. It also works for NumPy arrays.

    :param \\*args: objects containing numbers
    :returns: a flattened tuple of the rounded, `int`-converted items of
              `*args`

    >>> tir([1.24, -1.87])
    (1, -2)
    >>> tir([1.24, [-1.87]], 2.79)
    (1, -2, 3)
    """
    values = dh.utils.flatten(*args)
    return tuple(int(round(value)) for value in values)
