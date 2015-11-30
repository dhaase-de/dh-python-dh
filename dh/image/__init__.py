"""
Functions for image handling, image processing, and computer vision.

All images are represented as NumPy arrays, and so NumPy is required for this
module. All other image-related modules (e.g., scikit-image, OpenCV) are
optional (though some features might not work if they are not present).
"""

import numpy as np

# check if OpenCV is available
try:
    import cv2
    _HAVE_CV2 = True
except ImportError:
    _HAVE_CV2 = False

# check if PIL is available
try:
    import PIL
    import PIL.ImageTk
    _HAVE_PIL = True
except ImportError:
    _HAVE_PIL = False

# check if matplotlib is available
try:
    import matplotlib.pyplot as plt
    _HAVE_PLT = True
except ImportError:
    _HAVE_PLT = False

# check if scikit-image is available
try:
    import skimage
    import skimage.io
    _HAVE_SKIMAGE = True
except ImportError:
    _HAVE_SKIMAGE = False

# check if Tkinter is available
try:
    import tkinter
    import tkinter.ttk
    _HAVE_TKINTER = True
except ImportError:
    _HAVE_TKINTER = False

import dh.image.viewer
import dh.utils


##
## visualization
##


def normalize(I, mode="minmax", **kwargs):
    """
    Normalizes the image `I`.

    Supported NumPy data types are `uint8`, `uint16`, and all float types.
    """

    if mode == "none":
        return I

    elif mode == "interval":
        # interval range to be spread out to the "full" interval range
        (lower, upper) = sorted((kwargs["lower"], kwargs["upper"]))

        # the "full" interval range depends on the image's data type
        if I.dtype == "uint8":
            # 8 bit image
            lowerFull = 0
            upperFull = 255
        elif I.dtype == "uint8":
            # 16 bit image
            lowerFull = 0
            upperFull = 65535
        elif np.issubdtype(I.dtype, "float"):
            # float image
            lowerFull = 0.0
            upperFull = 1.0
        else:
            raise ValueError("Unsupported data type '{dtype}'".format(dtype=str(I.dtype)))

        # we temporarily work with a float image (because values outside of
        # the target interval can occur)
        T = I.astype("float32").copy()

        # spread the given interval to the full range, clip outlier values
        T = dh.utils.tinterval(T, lower, upper, lowerFull, upperFull)
        T = np.clip(T, a_min=lowerFull, a_max=upperFull, out=T)

        # return an image with the original data type
        return T.astype(I.dtype)

    elif mode == "minmax":
        return normalize(I, mode="interval", lower=np.min(I), upper=np.max(I))

    elif mode == "percentile":
        # get percentile
        try:
            q = float(kwargs["q"])
        except KeyError:
            q = 2.0
        q = dh.utils.sclip(q, 0.0, 50.0)
        return normalize(I, mode="interval", lower=np.percentile(I, q), upper=np.percentile(I, 100.0 - q))

    else:
        raise ValueError("Invalid mode '{mode}'".format(mode=mode))


def imstack():
    """
    Stack images into one image.
    """

    raise NotImplementedError("TODO")


def pinfo(I):
    """
    Prints info about the image `I`.
    """

    raise NotImplementedError("TODO")


def imshow(I, normalization="none", backends=("plt", "skimage"), **kwargs):
    """
    Displays the image on the screen.
    """

    viewer = dh.image.viewer.Viewer()
    viewer.view(I)

    # search for available backend (thirdparty module) for image display, in given order
    if False:
        # normalize image
        N = normalize(I, mode=normalization, **kwargs)        
        
        for backend in backends:
            if (backend == "plt") and _HAVE_PLT:
                #plt.ion()
                plt.imshow(N)
                plt.show()
                #plt.draw()
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
