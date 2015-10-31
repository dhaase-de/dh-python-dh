def isIterable(x):
    try:
        _ = (item for item in x)
        return True
    except TypeError:
        return False

def flatten(*args):
    for arg in args:
        try:
            # arg is iterable
            for item in arg:
                for item2 in flatten(item):
                    yield item2
        except TypeError:
            # x is not iterable
            yield arg

