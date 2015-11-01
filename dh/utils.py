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
    
    >>> list(flatten([[1], ['two'], [3.0], [None]]))
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

if __name__ == "__main__":
    print(list(flatten(1, [2], [3, 4], [5, [6]])))
    print(list(flatten( 1, "2", None, 3.0, int, {"x": 7} )))
