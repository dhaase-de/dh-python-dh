"""
General utility functions.
"""

import base64
import colorsys
import hashlib
import pickle


##
## iterable-related
##


def cycle(x, length):
    """
    Cycles through the values of `x` until `length` items were yielded.
    
    :param x: an iterable
    :yields: next recycled item of `x`
    
    >>> list(cycle([1, 2, 3], 5))
    [1, 2, 3, 1, 2]
    
    >>> list(cycle((i for i in range(1, 4)), 5))
    [1, 2, 3, 1, 2]
    
    .. todo:: handle non-list arguments more efficiently (avoid list() for entire `x`)
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
    Recursively flattens the items of all arguments into one iterable.

    :param \\*args: objects which are to be flattened
    :yields: next item of the flattened objects

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
    Zips the two halves of the object.
    
    :param x: Object to be "halved" and zipped.
    :returns: A `zip` object.
    
    >>> list(hzip([1, 2, 3, 4, 5, 6]))
    [(1, 4), (2, 5), (3, 6)]
    """

    N = len(x)
    M = int(N // 2)
    return zip(x[0:M], x[M:N])


def unique(x):
    """
    Yields unique values of `x`, preserving the order of the items.

    It also works for one-dimensional NumPy arrays. However, for NumPy arrays,
    :func:`numpy.unique` should be used.

    :param x: an iterable
    :yields: next unique item of `x`

    >>> list(unique((1, 2, 1, 3)))
    [1, 2, 3]

    >>> list(unique((1, 1.0, '1')))
    [1, '1']
    """

    seen = []
    for item in x:
        if item not in seen:
            yield item
            seen.append(item)


def which(x):
    """
    Yields the indices of the items which evaluate to `True`.

    :param x: an iterable
    :yields: index of the next item of `x` which evaluates to `True`

    >>> list(which((True, False, True, True)))
    [0, 2, 3]

    >>> list(which((1, 0, 1.0, 0.0, "a", "", None)))
    [0, 2, 4]
    """

    for (index, item) in enumerate(x):
        if item:
            yield index


##
## hashing
##


def ohash(x, outputFormat = "hex", byteCount = 64):
    """
    Hash any serializable object.
    
    :param x: A serializable object.
    :param outputFormat: Determines how to convert the hash output. Can be
        `'raw'` (or `'bytes'`), `'base2'` (or `'bin'`), `'base10'` (or `'int'`),
        `'base16'` (or `'hex'`), `'base32'`, or `'base64'`.
    :param byteCount: Number of bytes to use from the hash output. Must be
         between 1 and 64.
    :returns: The formatted hash. The type varies based on `outputFormat`.
    
    >>> ohash({'x': 1, 'y': 'two', 'z': [3.0]}, 'hex', 4)
    'ebad0cc2'
    
    >>> ohash({'x': 1, 'y': 'two', 'z': [3.0]}, 'int', 2)
    59247
    """
    
    # serialize the object and hash the serialization string (512 bits = 64 bytes)
    xSerialized = pickle.dumps(x, protocol = 0)
    hashBytes = hashlib.sha512(xSerialized).digest()
    
    # reduce byte count (repeatedly XOR the two halves of the byte array until the desired length is reached)
    if byteCount not in (1, 2, 4, 8, 16, 32, 64):
        raise ValueError("Invalid byte count ({}), must be in (1, 2, 4, 8, 16, 32, 64)".format(byteCount))
    while len(hashBytes) > byteCount:
        hashBytesReduced = b""
        for (int1, int2) in hzip(hashBytes):
            hashBytesReduced += (int1 ^ int2).to_bytes(1, byteorder = "big", signed = False)
        hashBytes = hashBytesReduced
        
    # format output
    if outputFormat in ("raw", "bytes"):
        hashFormatted = hashBytes
    elif outputFormat in ("base2", "bin"):
        hashFormatted = "".join(bin(hashByte)[2:].zfill(8) for hashByte in hashBytes)
    elif outputFormat in ("base10", "int"):
        hashFormatted = int.from_bytes(hashBytes, byteorder = "big", signed = False)
    elif outputFormat in ("base16", "hex"):
        hashFormatted = base64.b16encode(hashBytes).decode("ascii").lower()
    elif outputFormat in ("base32",):
        hashFormatted = base64.b32encode(hashBytes).decode("ascii")
    elif outputFormat in ("base64",):
        hashFormatted = base64.b64encode(hashBytes).decode("ascii")
    elif outputFormat in ("float", "color"):
        hashFloat = int.from_bytes(hashBytes, byteorder = "big", signed = False) / 2**(8 * byteCount)
        if outputFormat in ("float",):
            hashFormatted = hashFloat
        elif outputFormat in ("color",):
            hashFormatted = colorsys.hsv_to_rgb(hashFloat, 1.0, 1.0)
    else:
        raise ValueError("Invalid output format '{}'".format(outputFormat))
        
    return hashFormatted       

