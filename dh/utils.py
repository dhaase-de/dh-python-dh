"""
General utility functions.
"""

import base64
import colorsys
import hashlib
import math
import pprint
import time


##
## iterable-related
##


def cycle(x, length):
    """
    Cycles through the values of `x` until `length` items were yielded.

    >>> list(cycle([1, 2, 3], 5))
    [1, 2, 3, 1, 2]

    >>> list(cycle((i for i in range(1, 4)), 5))
    [1, 2, 3, 1, 2]

    .. seealso:: :func:`itertools.cycle` and :func:`itertools.repeat` (they
                 are similar but different).

    .. todo:: handle non-list arguments more efficiently (avoid list() for
              entire `x`)
    """

    # if items can't be accessed by index, create list from x
    if hasattr(x, "__getitem__") and hasattr(x, "__len__"):
        xList = x
    else:
        xList = list(x)

    # cycle loop
    M = len(xList)
    N = length
    for n in range(N):
        yield xList[n % M]


def flatten(*args):
    """
    Recursively flattens the items of `*args` into one iterable.

    >>> list(flatten(1, [2, 3, [4]]))
    [1, 2, 3, 4]

    >>> list(flatten([[1, []], ('two', [[3.0]]), (None,)]))
    [1, 'two', 3.0, None]
    """

    for arg in args:
        try:
            if isinstance(arg, str):
                raise TypeError()

            # arg is iterable (and not a string)
            for item in arg:
                for item2 in flatten(item):
                    yield item2
        except TypeError:
            # x is not iterable (or a string)
            yield arg


def hzip(x):
    """
    Zips the first and second half of `x`.

    >>> list(hzip([1, 2, 3, 4, 5, 6]))
    [(1, 4), (2, 5), (3, 6)]
    """

    N = len(x)
    M = int(N // 2)
    return zip(x[0:M], x[M:N])


def unique(x):
    """
    Yields unique values of `x`, preserving the order of the items.

    >>> list(unique((1, 2, 1, 3)))
    [1, 2, 3]

    >>> list(unique((1, 1.0, '1', 'one')))
    [1, '1', 'one']

    .. seealso:: :func:`numpy.unique` for NumPy arrays.
    """

    seen = []
    for item in x:
        if item not in seen:
            yield item
            seen.append(item)


def which(x):
    """
    Yields the indices of the items which evaluate to `True`.

    >>> list(which((True, False, True, True)))
    [0, 2, 3]

    >>> list(which((1, 0, 1.0, 0.0, "a", "", None)))
    [0, 2, 4]
    """

    for (index, item) in enumerate(x):
        if item:
            yield index


##
## math
##


# adaptive round
def around(number, significantDigitCount=3):
    """
    Rounds a number to the first `significantDigitCount` digits after the
    appearance of the first non-zero digit ("adaptive round").

    >>> around(1234.56789, 3)
    1230.0

    >>> around(0.00123456789, 3)
    0.00123
    """

    try:
        magnitude = math.floor(math.log10(abs(number)))
    except ValueError:
        magnitude = 0
    digitCount = int(significantDigitCount - magnitude - 1)
    return round(number, digitCount)


##
## hashing
##


def ohash(x, outputFormat="hex", byteCount=64):
    """
    Hash any serializable object.

    `outputFormat` determines how to convert the hash output. It can be
    `'raw'` (or `'bytes'`), `'base2'` (or `'bin'`), `'base10'` (or `'int'`),
    `'base16'` (or `'hex'`), `'base32'`, or `'base64'`.
    `byteCount` specifies the number of bytes to use from the hash output. It
    must be in (1, 2, 4, 8, 16, 32, 64).

    >>> ohash({'x': 1, 'y': 'two', 'z': [3.0, None]}, 'hex', 4)
    'f2e79df1'

    >>> ohash({'x': 1, 'y': 'two', 'z': [3.0, None]}, 'int', 2)
    28438
    """

    # serialize the object and hash the serialization string (512 bits = 64 bytes)
    # note pickle.dumps is not used here as it sometimes gave different results for identical objects
    #xSerialized = pickle.dumps(x, protocol=0)
    xSerialized = pprint.pformat(x).encode("utf-8")
    hashBytes = hashlib.sha512(xSerialized).digest()

    # reduce byte count (repeatedly XOR the two halves of the byte array until the desired length is reached)
    if byteCount not in (1, 2, 4, 8, 16, 32, 64):
        raise ValueError("Invalid byte count ({}), must be in (1, 2, 4, 8, 16, 32, 64)".format(byteCount))
    while len(hashBytes) > byteCount:
        hashBytesReduced = b""
        for (int1, int2) in hzip(hashBytes):
            hashBytesReduced += (int1 ^ int2).to_bytes(1, byteorder="big", signed=False)
        hashBytes = hashBytesReduced

    # format output
    if outputFormat in ("raw", "bytes"):
        hashFormatted = hashBytes
    elif outputFormat in ("base2", "bin"):
        hashFormatted = "".join(bin(hashByte)[2:].zfill(8) for hashByte in hashBytes)
    elif outputFormat in ("base10", "int"):
        hashFormatted = int.from_bytes(hashBytes, byteorder="big", signed=False)
    elif outputFormat in ("base16", "hex"):
        hashFormatted = base64.b16encode(hashBytes).decode("ascii").lower()
    elif outputFormat in ("base32",):
        hashFormatted = base64.b32encode(hashBytes).decode("ascii")
    elif outputFormat in ("base64",):
        hashFormatted = base64.b64encode(hashBytes).decode("ascii")
    elif outputFormat in ("float", "color"):
        hashFloat = int.from_bytes(hashBytes, byteorder="big", signed=False) / 2**(8 * byteCount)
        if outputFormat in ("float",):
            hashFormatted = hashFloat
        elif outputFormat in ("color",):
            hashFormatted = colorsys.hsv_to_rgb(hashFloat, 1.0, 1.0)
    else:
        raise ValueError("Invalid output format '{}'".format(outputFormat))

    return hashFormatted


##
## decorators
##


def info(f):
    def g(*args, **kwargs):
        t0 = time.time()
        res = f(*args, **kwargs)
        t1 = time.time()

        
        # format args and result objects
        def oformat(x):
            P = pprint.PrettyPrinter(compact=True)
            xStr = P.pformat(x)
            if len(xStr) > 60:
                xStr = "..."
            return xStr        
        
        strArgs = oformat(args)
        strKwargs = oformat(kwargs)
        strRes = oformat(res)
        
        allArgs = (args, kwargs)
        hashArgs = ohash(allArgs, "hex", 4)        
        hashRes = ohash(res, "hex", 4)
        
        dt = max(0.0, t1 - t0)
        #print("@info({f}(h({args} = <0x{hashArgs}>))) -> hash({res}) = <0x{hashRes}> took {dt} seconds".format(f = f.__name__, dt = around(dt, 3)))
        print("@info({fName}):".format(fName = f.__name__))
        print("  Arguments:")
        print("    args:    {args}".format(args=strArgs))
        print("    kwargs:  {kwargs}".format(kwargs=strKwargs))
        print("    ohash:   {hashArgs}".format(hashArgs=hashArgs))
        print("  Result:")
        print("    value:   {res}".format(res=strRes, hashRes=hashRes))
        print("    ohash:   {hashRes}".format(res=strRes, hashRes=hashRes))
        print("  Time:      {dt} seconds".format(dt=around(dt, 3)))
        
        return res
    return g

