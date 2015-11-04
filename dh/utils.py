"""
General utility functions.
"""


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

