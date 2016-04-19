"""
Functions for image handling, image processing, and computer vision.

All images are represented as NumPy arrays (in the form `I[y, x]` for gray
scale images and `I[y, x, channel]` for color images), and so NumPy (but only
NumPy) is required for this module. Image-related functions which require
further thirdparty modules (e.g., scikit-image, OpenCV, mahotas, PIL) are
optional.
"""

import collections
import glob
import json
import os.path

import numpy as np
import numpy.fft

import dh.gui
import dh.utils


##
## check for optional thirdparty image processing modules
##


# OpenCV
try:
    import cv2
    _HAVE_CV2 = True
except ImportError:
    _HAVE_CV2 = False

# scikit-image
try:
    import skimage
    _HAVE_SKIMAGE = True
except ImportError:
    _HAVE_SKIMAGE = False

# mahotas
try:
    import mahotas
    _HAVE_MAHOTAS = True
except ImportError:
    _HAVE_MAHOTAS = False


##
## load, save, show
##


def imread(filename, gray=True):
    """
    Load image from file `filename` and return NumPy array.

    If `gray` is `True`, a grayscale image is returned. If `gray` is `False`,
    then a color image is returned (in RGB order), even if the original image
    is grayscale.
    """

    # OpenCV
    if _HAVE_CV2:
        # flags - if `gray` is False, the
        flags = cv2.IMREAD_ANYDEPTH | (cv2.IMREAD_GRAYSCALE if gray else cv2.IMREAD_COLOR)

        # read image
        I = cv2.imread(filename=filename, flags=flags)

        # BGR -> RGB
        if not gray:
            I = I[:,:,::-1]

        return I

    # scikit-image
    #if _HAVE_SKIMAGE:
    #    I = skimage.io.imread(fname=filename, )
    #    return I

    raise RuntimeError("Found no module for this operation")


def imshow(I, wait=0, scale=None, windowName="imshow"):
    """
    Show image on the screen.
    """

    if not _HAVE_CV2:
        raise RuntimeError("Need OpenCV module ('cv2') for this functionality")

    # scale of the image
    if scale is None:
        (W, H) = dh.gui.screenres()
        if (W is not None) and (H is not None):
            scale = 0.85 * min(H / I.shape[0], W / I.shape[1])
        else:
            scale = 850.0 / max(I.shape)
    interpolationType = cv2.INTER_CUBIC if scale > 1.0 else cv2.INTER_NEAREST

    # resized image
    S = cv2.resize(I, None, None, scale, scale, interpolationType)

    # RGB -> BGR
    if iscolor(S):
        S = S[:,:,::-1]

    cv2.imshow(windowName, S)
    key = cv2.waitKey(wait)

    return key


def imwrite(filename, I):
    """
    Write image `I` to file `filename`.
    """

    # TODO: also cover case of .npy and .npz files

    # OpenCV
    if _HAVE_CV2:
        # BGR -> RGB
        if iscolor(I):
            J = I[:,:,::-1]
        else:
            J = I

        # write
        cv2.imwrite(filename=filename, img=J)

        return

    raise RuntimeError("Found no module for this operation")


##
## type conversion
##


def trange(dtype):
    """
    Returns the range (min, max) of valid intensity values for an image of
    NumPy type string `dtype`.

    Allowed types are `'uint8'`, `'uint16'`, and any float type (e.g.,
    `'float32'`, `'float64'`). The range for each data types follows the
    convention of the OpenCV library.

    >>> trange('uint8')
    (0, 255)
    >>> trange('float32')
    (0.0, 1.0)
    """

    if dtype == "uint8":
        return (0, 255)
    elif dtype == "uint16":
        return (0, 65535)
    elif np.issubdtype(dtype, "float"):
        return (0.0, 1.0)
    else:
        raise ValueError("Invalid image type '{dtype}'".format(dtype=dtype))


def convert(I, dtype):
    """
    Converts image `I` to NumPy type given by the string `dtype` and scales the
    intensity values accordingly.
    """

    if I.dtype == dtype:
        return I.copy()
    else:
        scale = trange(dtype)[1] / trange(I.dtype)[1]
        return (I.astype("float") * scale).astype(dtype)


##
## color conversion
##


def nchannels(I):
    """
    Return the number of color channels of the image `I`.
    """

    D = len(I.shape)
    if D == 2:
        return 1
    elif D == 3:
        return I.shape[-1]
    else:
        raise ValueError("Urecognized image array shape")


def isgray(I):
    """
    Returns true if the image `I` is in gray-scale mode (i.e., if it has one
    color channel).
    """

    return (nchannels(I) == 1)


def iscolor(I):
    """
    Returns true if the image `I` is in color mode (i.e., if it has three
    color channels).
    """

    return (nchannels(I) == 3)


def asgray(I):
    """
    Convert image `I` to gray-scale mode.
    """

    if isgray(I):
        # nothing to convert, just make sure that the image shape is consistent
        D = len(I.shape)
        if D == 2:
            return I
        elif D == 3:
            return I[:, :, 0]
    else:
        return np.mean(I, axis=2).astype(I.dtype)


def ascolor(I):
    """
    Convert image `I` to color (RGB) mode.
    """

    if iscolor(I):
        # nothing to convert, just make sure that the image shape is consistent
        return I
    else:
        return np.dstack((I,) * 3)


# path into which setup.py installs all colormap files
_COLORMAP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "colormaps"))


def colormap(c):
    """
    If `c` is a dict, it is assumed to be a valid colormap (see below) and is
    returned. Otherwise, `c` is interpreted as colormap name (not as filename)
    and is loaded from the colormap dir.

    A colormap is a dict, where the keys are 8 bit unsigned gray values which
    are mapped to 8 bit unsigned 3-tuples (RGB) each.
    """

    if isinstance(c, dict):
        # `c` is already a dict and assumed to be a valid colormap
        m = c
    else:
        # `c` is interpreted as colormap name, and the dict is loaded from the colormap dir
        filename = os.path.join(_COLORMAP_DIR, "{}.{}".format(c.lower(), "json"))
        with open(filename, "r") as f:
            m = json.load(f)

    # json stores dict keys as strings, so we must convert them to ints
    return {int(key): tuple(value) for (key, value) in m.items()}


def colorize(I, c="jet", reverse=False, bitwise=False):
    """
    Colorize image `I` according to the colormap `c` and return 8 bit image.

    `c` can either be a colormap dict or a colormap name, see
    :func:`dh.image.colormap`.

    .. seealso:: :func:`dh.image.colormap` for how to specify `c`
    """

    # make sure that the input has only two dimensions
    # it could also have three dimensions, with the length of the last
    # dimension being one
    if not isgray(I):
        raise ValueError("Input image must be in gray scale mode")
    J = asgray(I).copy()

    if reverse:
        J = 255 - J

    # mapping from source (one channel) to target (three channel) color
    m = colormap(c)

    # empty color image
    C = ascolor(np.zeros_like(J))

    # apply mapping defined by colormap dict
    for (source, target) in sorted(m.items()):
        if bitwise:
            M = ((J & source) > 0)
        else:
            M = (J == source)
        for nChannel in range(3):
            C[:,:,nChannel][M] = target[nChannel]

    return C


def colormaps(show=True, **kwargs):
    """
    Creates and returns a demo image of all available colormaps.
    """

    slope = np.array([range(256)] * 32, dtype = "uint8")

    filenames = glob.glob(os.path.join(_COLORMAP_DIR, "*.json"))
    names = (os.path.splitext(os.path.basename(filename))[0] for filename in filenames)
    Is = []
    for name in sorted(names):
        I = colorize(slope, name)
        Is.append(I)

    C = np.vstack(Is)
    if show:
        imshow(C, **kwargs)

    return {
        "names": names,
        "image": C,
    }


##
## geometric transformations
##


def shift(I, dx=0, dy=None):
    """
    Shifts the pixels of the image `I` by `dx` and `dy` along the x and y axes.

    For each of `dx` and `dy`: if the value is an integer, it is interpreted
    as the number of pixels by which to shift. If the value is a float, it is
    interpreted as fraction of the image shape of the according axis.
    """

    # by default dy is equal to dx
    if dy is None:
        dy = dx

    # float values are interpreted as fractions of the image shape
    if isinstance(dx, float):
        dx = int(I.shape[1] * dx)
    if isinstance(dy, float):
        dy = int(I.shape[0] * dy)

    # shift
    S = I.copy()
    S = np.roll(S, dy, axis=0)
    S = np.roll(S, dx, axis=1)
    return S


def rotate(I, degree):
    """
    Rotate the image `I` counter-clock-wise by the angle specified by `degree`.

    Valid values for the angle are `0`, `90`, `180`, and `270`.
    """

    degree = int(degree) % 360
    if degree not in (0, 90, 180, 270):
        raise ValueError("Unsupported rotation angle")
    k = degree // 90
    if k > 0:
        return np.rot90(I, k)
    else:
        return I


##
## pixel-wise operations
##


def identity(I):
    """
    Returns the input image `I`.

    This function is useful in image processing pipelines, in cases where a
    no-op is needed.
    """

    return I


def invert(I):
    """
    Inverts the intensities of all pixels.
    """

    (_, typeMax) = trange(I.dtype)
    return (typeMax - I)


def log(I, normalization="minmax", **kwargs):
    """
    Perform the logarithm transform to the pixel intensities of the image `I`.
    """

    (typeMin, _) = trange(I.dtype)

    J = I.copy()
    J[J == typeMin] = typeMin + 1
    F = convert(J, "float")
    L = np.log(F)
    N = normalize(L, mode=normalization, **kwargs)
    return convert(N, I.dtype)


def gamma(I, gamma, inverse=False):
    """
    Perform power-law conversion with exponent `gamma` (or one over `gamma` if
    `inverse` is true) of the intensities of image `I`.
    """

    exponent = gamma if not inverse else (1.0 / gamma)
    F = convert(I, "float")
    G = np.power(F, exponent)
    return convert(G, I.dtype)


def threshold(I, theta, relative=False):
    """
    Apply the absolute threshold `theta` to the image `I`.

    If `relative` is true, the threshold is multiplied by the maximum possible
    value for the given image type.
    """

    (typeMin, typeMax) = trange(I.dtype)
    if relative:
        theta *= typeMax
    T = I.copy()
    T[I <= theta] = typeMin
    T[I > theta] = typeMax
    return T


def normalize(I, mode="minmax", **kwargs):
    """
    Normalizes the intensity values of the image `I`.

    .. seealso:: :func:`dh.image.trange` for allowed image data types.
    """

    if mode == "none":
        return I

    elif mode == "interval":
        # interval range to be spread out to the "full" interval range
        (lower, upper) = sorted((kwargs["lower"], kwargs["upper"]))

        # the "full" interval range depends on the image's data type
        (lowerFull, upperFull) = trange(I.dtype)

        # we temporarily work with a float image (because values outside of
        # the target interval can occur)
        T = I.astype("float").copy()

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


##
## frequency domain
##


def fft(I):
    F = np.fft.fftshift(np.fft.fft2(I))
    #Re, Im
    #Theta, Phase
    return np.abs(F)**2
    #return np.angle(F)


def selffiltering():
    raise NotImplementedError("TODO")


##
## visualization
##


def imstack(Is):
    """
    Stack images `Is` into one image.
    """

    raise NotImplementedError("TODO")


def pinfo(I):
    """
    Prints info about the image `I`.
    """

    info = collections.OrderedDict()
    info["shape"] = I.shape
    #info["shape (squeezed)"] = I.squeeze().shape
    info["elements"] = np.prod(I.shape)
    info["dtype"] = I.dtype
    info["mean"] = np.mean(I)
    info["std"] = np.std(I)
    info["min"] = np.min(I)
    info["1st quartile"] = np.percentile(I, 25.0)
    info["median"] = np.median(I)
    info["3rd quartile"] = np.percentile(I, 75.0)
    info["max"] = np.max(I)
    counter = collections.Counter(I.flatten().tolist())
    (counterArgmax, counterMax) = counter.most_common(1)[0]
    info["mode"] = "{} ({}%)".format(counterArgmax, round(100.0 * counterMax / info["elements"], 2))

    print("=" * 40)
    maxKeyLength = max(len(key) for key in info.keys())
    for key in info.keys():
        print(("{key:.<" + str(maxKeyLength) + "} = {value}").format(key=(key + " ")[:maxKeyLength], value=info[key]))

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
