"""
Functions for image handling, image processing, and computer vision.

All images are represented as NumPy arrays (in the form `I[y, x]` for gray
scale images and `I[y, x, channel]` for color images, with RGB channel order),
and so NumPy (but only NumPy) is required for this module. Image-related
functions which require further thirdparty modules (e.g., OpenCV, scikit-image,
mahotas, PIL) are optional.
"""

import collections
import glob
import json
import os.path

import numpy as np

import dh.gui
import dh.utils


###
#%% optional thirdparty modules
###


# try to import OpenCV
try:
    import cv2
    _CV2_VERSION = cv2.__version__
    _CV2_ERROR = None
except ImportError as e:
    _CV2_VERSION = None
    _CV2_ERROR = e


# decorator for functions that need OpenCV
def CV2(f):
    if _CV2_VERSION is None:
        raise RuntimeError("Module 'cv2' is needed for that operation ('{}'), but could not be imported (error: {})".format(f.__name__, _CV2_ERROR))

    def g(*args, **kwargs):
        return f(*args, **kwargs)

    return g


# skimage
# mahotas


###
#%% load, save, show
###


@CV2
def imread(filename, color=False):
    """
    Load image from file `filename` and return NumPy array.

    If `color` is `False`, a grayscale image is returned. If `color` is `True`,
    then a color image is returned (in RGB order), even if the original image
    is grayscale.
    """

    # check if file exists
    if not os.path.exists(filename):
        raise RuntimeError("Image file '{}' does not exist".format(filename))

    # flags - select grayscale or color mode
    flags = cv2.IMREAD_ANYDEPTH | (cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE)

    # read image
    I = cv2.imread(filename=filename, flags=flags)

    # BGR -> RGB
    if color:
        I = I[:, :, ::-1]

    return I


@CV2
def imwrite(filename, I, mkpdir=True):
    """
    Write image `I` to file `filename`.

    If `mkpdir` is `True`, the parent dir of the given filename is created
    before saving the image.
    """

    # TODO: also cover case of .npy and .npz files

    # create parent dir
    if mkpdir:
        dh.utils.mkpdir(filename)

    # BGR -> RGB
    if iscolor(I):
        J = I[:, :, ::-1]
    else:
        J = I

    # write
    return cv2.imwrite(filename=filename, img=J)


@CV2
def imshow(I, wait=0, scale=None, invert=False, colormap=None, windowName="imshow"):
    """
    Show image on the screen.
    """

    # scale of the image
    if scale is None:
        (W, H) = dh.gui.screenres()
        if (W is not None) and (H is not None):
            scale = 0.85 * min(H / I.shape[0], W / I.shape[1])
        else:
            scale = 850.0 / max(I.shape)
    interpolationType = cv2.INTER_CUBIC if scale > 1.0 else cv2.INTER_NEAREST

    # convert to 8 bit
    J = convert(I, "uint8")

    # resized image
    J = cv2.resize(J, None, None, scale, scale, interpolationType)

    # invert
    if invert:
        J = dh.image.invert(J)

    # apply colormap
    if colormap is not None:
        J = colorize(asgray(J), c=colormap)

    # RGB -> BGR (for OpenCV)
    if iscolor(J):
        J = J[:,:,::-1]

    cv2.imshow(windowName, J)
    key = cv2.waitKey(wait)

    return key


def stack(Is, dtype=None, gray=None):
    """
    Stack images given by `Is` into one image.

    `Is` must be a vector of vectors of images, defining rows and columns.
    """

    # find common data type and color mode
    if dtype is None:
        dtype = tcommon((I.dtype for row in Is for I in row))
    if gray is None:
        gray = all(isgray(I) for row in Is for I in row)

    # step 1/2: construct stacked image for each row
    Rs = []
    width = 0
    for row in Is:
        # height of the row
        rowHeight = 0
        for I in row:
            rowHeight = max(rowHeight, I.shape[0])

        R = None
        for I in row:
            # convert to common data type and color mode
            if gray:
                J = asgray(I)
            else:
                J = ascolor(I)
            J = convert(J, dtype)

            # ensure that image has the height of the row
            gap = rowHeight - J.shape[0]
            if gap > 0:
                if gray:
                    Z = np.zeros(shape=(gap, J.shape[1]), dtype=dtype)
                else:
                    Z = np.zeros(shape=(gap, J.shape[1], 3), dtype=dtype)
                J = np.vstack((J, Z))

            # add to current row image
            if R is None:
                R = J
            else:
                R = np.hstack((R, J))

        width = max(width, R.shape[1])
        Rs.append(R)

    # step 2/2: construct stacked image from the row images
    S = None
    for R in Rs:
        # ensure that the row image has the width of the final image
        gap = width - R.shape[1]
        if gap > 0:
            if gray:
                Z = np.zeros(shape=(R.shape[0], gap), dtype=dtype)
            else:
                Z = np.zeros(shape=(R.shape[0], gap, 3), dtype=dtype)
            R = np.hstack((R, Z))

        # add to final image
        if S is None:
            S = R
        else:
            S = np.vstack((S, R))

    return S


###
#%% type conversion
###


def eqtype(I, J):
    """
    Ensure that `I` and `J` have the same NumPy type.

    If both images have the same type, returns the type name as string.
    Otherwise, a `ValueError` is raised.
    """

    if I.dtype != J.dtype:
        raise ValueError("Images have different NumPy types ('{}', '{}')".format(I.dtype, J.dtype))
    else:
        return I.dtype


def tcommon(dtypes):
    """
    For a given vector `dtypes` of types, returns the type which supports
    all ranges.

    >>> tcommon(['bool', 'uint8', 'uint16'])
    'uint16'
    >>> tcommon(['uint8', 'bool'])
    'uint8'
    >>> tcommon(['uint8', 'uint8'])
    'uint8'
    >>> tcommon(['uint8', 'uint16'])
    'uint16'
    >>> tcommon(['uint8', 'float'])
    'float'
    """

    hierarchy = ("bool", "uint8", "uint16", "float")
    maxIndex = 0
    for dtype in dtypes:
        try:
            index = hierarchy.index(dtype)
        except ValueError:
            raise RuntimeError("Invalid image type '{dtype}'".format(dtype=dtype))
        maxIndex = max(maxIndex, index)

    return hierarchy[maxIndex]


def trange(dtype):
    """
    Returns the range (min, max) of valid intensity values for an image of
    NumPy type string `dtype`.

    Allowed types are `'bool'`, `'uint8'`, `'uint16'`, and any float type
    (e.g., `'float32'`, `'float64'`). The range for each data types follows the
    convention of the OpenCV library.

    >>> trange('uint8')
    (0, 255)
    >>> trange('float32')
    (0.0, 1.0)
    """

    if dtype is None:
        # np.issubdtype(None, "float") is True, therefore we have to check for this error here explicitly
        raise ValueError("Invalid image type '{dtype}'".format(dtype=dtype))
    elif dtype == "bool":
        return (False, True)
    elif dtype == "uint8":
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

    Intensity values are always clipped to the allowed range (even for
    identical source and target types). Returns always a copy of the data, even
    for equal source and target types.
    """

    # clip image against its source dtype (important for floats)
    (tLower, tUpper) = trange(I.dtype)
    J = clip(I, tLower, tUpper)

    if I.dtype == dtype:
        return J
    else:
        scale = trange(dtype)[1] / trange(I.dtype)[1]
        return (J.astype("float") * scale).astype(dtype)


###
#%% color conversion
###


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
        # nothing to convert
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
    names = list(sorted(os.path.splitext(os.path.basename(filename))[0] for filename in filenames))
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


###
#%% pixel-wise operations
###


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


def clip(I, lower=None, upper=None):
    """
    Clips the image pixel values to the interval [`lower`, `upper`], and
    preserves the image type.

    Always returns a copy of the data, even if both interval ends are `None`.
    """

    J = I.copy()
    dtype = J.dtype
    (tLower, tUpper) = trange(dtype)
    if lower is not None:
        J = np.maximum(I, np.array((dh.utils.sclip(lower, tLower, tUpper),), dtype=dtype))
    if upper is not None:
        J = np.minimum(J, np.array((dh.utils.sclip(upper, tLower, tUpper),), dtype=dtype))
    return J


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


###
#%% frequency domain
###


def selffiltering():
    raise NotImplementedError("TODO")


###
#%% geometric transformations
###


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


###
#%% coordinates
###


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


###
#%% image-image operations
###


def imdiff(I, J):
    """
    Clipped image subtraction `I - J`.

    Both images need to have the same NumPy type. The result image has the same
    type as the input images and is clipped against the type's valid intensity
    range.
    """

    dtype = eqtype(I, J)
    X = convert(I, "float")
    Y = convert(J, "float")
    return convert(X - Y, dtype)


###
#%% development
###


def pinfo(I):
    """
    Prints info about the image `I`.
    """

    counter = collections.Counter(I.flatten().tolist())
    (counterArgmax, counterMax) = counter.most_common(1)[0]
    #("mode", "{} ({}%)".format(counterArgmax, round(100.0 * counterMax / info["elements"], 2))),

    info = (
        ("shape", I.shape),
        #("elements"], np.prod(I.shape)),
        ("dtype", I.dtype),
        ("mean", np.mean(I)),
        ("std", np.std(I)),
        ("min", np.min(I)),
        ("1st quartile", np.percentile(I, 25.0)),
        ("median", np.median(I)),
        ("3rd quartile", np.percentile(I, 75.0)),
        ("max", np.max(I)),
     )

    #print("=" * 40)
    #maxKeyLength = max(len(key) for key in info.keys())
    #for key in info.keys():
    #    print(("{key:.<" + str(maxKeyLength) + "} = {value}").format(key=(key + " ")[:maxKeyLength], value=info[key]))
    dh.utils.ptable(info)
