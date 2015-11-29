"""
Functions for image handling, image processing, and computer vision.

All images are represented as NumPy arrays, and so NumPy is required for this
module. All other image-related modules (e.g., scikit-image, OpenCV) are
optional (though some features might not work if they are not present).
"""

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_PLT = True
except ImportError:
    _HAVE_PLT = False

try:
    import skimage
    _HAVE_SKIMAGE = True
except ImportError:
    _HAVE_SKIMAGE = False

import dh.utils


##
## visualization
##


def normalize(I, mode="minmax"):
    """
    Normalizes the image `I`.
    """
    
    if mode == "none":
        return I
    elif mode == "minmax":
        T = I.astype("float32").copy()
        T = T - np.min(T)
        T = T / np.max(T)
        return T.astype(I.dtype)


def imshow(I, normalization="none", backends=("plt", "skimage")):
    """
    Shows the image.
    """

    # normalize image
    N = normalize(I, mode=normalization)

    # search for available backend (thirdparty module) for image display, in given order
    for backend in backends:
        if (backend == "plt") and _HAVE_PLT:
            plt.imshow(N)
            plt.show()
            break
        elif (backend == "skimage") and _HAVE_SKIMAGE:
            skimage.io.imshow(N)
            break
    else:
        raise RuntimeError("No backend available for image display")

##
## coordinates
##


def tir(*args):
    """
    The items of `*args` are flattened (via :func:`dh.utils.flatten`), rounded,
    converted to `int` and combined into a tuple.

    The primary use-case of this function is to pass point coordinates to
    certain OpenCV functions. It also works for NumPy arrays.

    >>> tir(1.24, -1.87)
    (1, -2)
    >>> tir([1.24, -1.87, 3.23])
    (1, -2, 3)
    """

    items = dh.utils.flatten(*args)
    return tuple(int(round(item)) for item in items)


def tirr(*args):
    """
    As :func:`dh.sci.tir`, but reverses the order of the items.

    When used to pass point coordinates to certain OpenCV functions, the item
    reversal means reversing the order of the axes (x,y -> y,x).

    >>> tirr(1.24, -1.87)
    (-2, 1)
    >>> tirr([1.24, -1.87, 3.23])
    (3, -2, 1)
    """

    items = dh.utils.flatten(*args)
    return tir(reversed(list(items)))


def hom(x):
    """
    Transforms `x` from Euclidean coordinates into a NumPy array of homogeneous
    coordinates.

    >>> hom([1.24, -1.87])
    array([ 1.24, -1.87,  1.  ])
    """

    return np.append(np.array(x), 1.0)


def unhom(x):
    """
    Transforms `x` from homogeneous coordinates into a NumPy array of Euclidean
    coordinates.

    >>> unhom([0.62 , -0.935,  0.5])
    array([ 1.24, -1.87])
    """

    return np.array(x[:-1]) / x[-1]


def hommap(M, x):
    """
    Transforms `x` to homogeneous coordinates, applies the linear mapping given
    by the matrix `M` and converts the result back to Euclidean coordinates.

    >>> M = np.eye(3)
    >>> M[0, 2] = 1.0
    >>> M[1, 2] = -2.0
    >>> hommap(M, [1.24, -1.87])
    array([ 2.24, -3.87])
    """

    return unhom(np.dot(M, hom(x)))
