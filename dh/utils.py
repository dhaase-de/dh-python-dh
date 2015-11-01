"""
General utility functions.
"""

def isIterable(x):
    try:
        _ = (item for item in x)
        return True
    except TypeError:
        return False

def flatten(*args):
    """
    Recursively flattens the items of all arguments into one iterable.

    :param \\*args: objects which are to be flattened
    :yields: next item of the flattened objects

    >>> list(flatten(1, [2], [[3]], [4, [5]]))
    [1, 2, 3, 4, 5]
    
    .. todo:: handle strings correctly
    """
    
    for arg in args:
        try:
            # arg is iterable
            for item in arg:
                for item2 in flatten(item):
                    yield item2
        except TypeError:
            # x is not iterable
            yield arg
