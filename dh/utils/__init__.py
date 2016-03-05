"""
General utility functions.

Written in pure Python, using only modules from the standard library to ensure
maximum compatibility.
"""

import base64
import collections
import colorsys
import errno
import functools
import hashlib
import importlib
import inspect
import math
import os
import pprint
import time


##
## general helpers
##


class avdict():
    """
    Class with (recursive) autovivification of attributes and items.

    Attributes and items of the same name refer to the same object.

    >>> d = avdict()
    >>> d.foo.bar.xyz = 123
    >>> d.foo.bar.xyz
    123
    >>> d["foo"].bar["xyz"]
    123
    """

    def __getitem__(self, key):
        """
        This is where the magic happens: if an attribute does not exists, it is
        created as an instance of this class.
        """

        if key not in self.__dict__:
            self.__dict__[key] = avdict()
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, attr):
        return self[attr]

    def todict(self):
        """
        Returns a nested dictionary resembling the structure of the instance.
        """

        d = {}
        for (key, value) in self.__dict__.items():
            if isinstance(value, type(self)):
                d[key] = value.todict()
            else:
                d[key] = value
        return d


def fsched(f, diff, timeout=None, stopOnException=True, *args, **kwargs):
    """
    Simple scheduler which repeatedly calls a function `f` with a fixed time
    interval `diff` (in seconds) between calls.

    The scheduler stops when a function call evaluates to false, or when
    `stopOnException` is true and the function call triggers an exception. If
    `timeout` (in seconds) is specified, the scheduler will raise a
    `RuntimeError` if it did not stop until this point. `*args` and `**kwargs`
    are passed to `f` for each call.

    .. seealso:: `sched.scheduler` for a more flexible scheduler.
    """

    timeNow = time.time()
    timeNext = timeNow
    if timeout is not None:
        timeTimeout = timeNow + timeout
    while True:
        # timeout?
        if (timeout is not None) and (timeNext >= timeTimeout):
            raise RuntimeError("Scheduler timed out")

        # sleep until next call is due and schedule next call
        timeNow = time.time()
        timeWait = max(timeNext - timeNow, 0.0)
        time.sleep(timeWait)
        timeNext = time.time() + diff

        # call function
        try:
            res = f(*args, **kwargs)
        except:
            if stopOnException:
                raise

        # stop if the function return value evaluates to false
        if not res:
            return


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


def eqvalue(x):
    """
    Checks whether all values of the iterable `x` are identical and returns
    that value if true, and otherwise raises a `ValueError` exception.

    >>> eqvalue([1, 1, 1])
    1
    """

    items = iter(x)
    first = next(items)
    for item in items:
        if item != first:
            raise ValueError("Values are not identical")
    return first


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
    Yields the indices of the items of `x` which evaluate to `True`.

    >>> list(which((True, False, True, True)))
    [0, 2, 3]

    >>> list(which((1, 0, 1.0, 0.0, "a", "", None)))
    [0, 2, 4]
    """

    for (index, item) in enumerate(x):
        if item:
            yield index


##
## file-related
##


def absdir(path):
    """
    Returns the absolute path of the directory name of `path`.
    """

    return os.path.abspath(os.path.dirname(path))


def mkdir(dirname):
    """
    Creates directory `dirname` if it does not exist already.

    .. seealso:: http://stackoverflow.com/a/5032238/1913780
    """

    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def mkpdir(filename):
    """
    Creates the parent directory of `filename` if it does not exists already.
    """

    mkdir(os.path.dirname(filename))


##
## formatting
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


def tstr(s, maxLength=80, ellipsis="..."):
    """
    Truncates the string `s` and adds ellipsis such that the returned string
    has at most `maxLength` characters, including the ellipsis.

    >>> tstr('The quick brown fox jumps over the lazy dog', 40)
    'The quick brown fox jumps over the la...'
    """

    if len(s) > maxLength:
        return s[:max(0, maxLength - len(ellipsis))] + ellipsis
    else:
        return s


def fargs(*args, **kwargs):
    """
    Format `*args` and `**kwargs` into one string resembling the original call.

    >>> fargs(1, [2], x=3.0, y='four')
    "1, [2], x=3.0, y='four'"

    .. note: The items of `**kwargs` are sorted by their key.
    """

    items = []
    for arg in args:
        items.append(pprint.pformat(arg))
    for kw in sorted(kwargs):
        items.append(kw + "=" + pprint.pformat(kwargs[kw]))
    return ", ".join(items)


def ftime(secs):
    """
    Format a time duration `secs` given in seconds into a human readable
    string.

    >>> ftime(12345)
    '3h25m45s'
    """

    units = ("d", "h", "m", "s")
    factors = (86400, 3600, 60, 1)

    res = ""
    if secs < 0.0:
        secs = abs(secs)
        res += "-"
    for (unit, factor) in zip(units, factors):
        value = int(math.floor(secs / factor))
        secs -= value * factor
        if (value > 0) or (unit == units[-1]):
            res += "{value}{unit}".format(value=value, unit=unit)

    return res


##
## math
##


def around(number, digitCount=3):
    """
    Rounds a number to the first `digitCount` digits after the appearance of
    the first non-zero digit ("adaptive round").

    >>> around(1234.56789, 3)
    1230.0

    >>> around(0.00123456789, 3)
    0.00123
    """

    try:
        magnitude = math.floor(math.log10(abs(number)))
    except ValueError:
        magnitude = 0
    roundDigitCount = int(digitCount - magnitude - 1)
    return round(number, roundDigitCount)


def cumsum(x):
    """
    Yields the cumulative sum of the elements of `x`.

    It works for any data type that supports addition (e.g., also fractions via
    `fractions.Fraction`).

    >>> list(cumsum([1, 4, 2, 3]))
    [1, 5, 7, 10]
    """

    c = None
    for item in x:
        if c is None:
            c = item
        else:
            c += item
        yield c


class odiff():
    """
    Returns the difference between the last two values that were added
    ("online difference").

    The first difference value to be returned is specified by `firstDiff`.

    >>> a = odiff(firstDiff=0)
    >>> a.update(3)
    0
    >>> a.update(7)
    4
    >>> a.update(4)
    -3
    >>> a.update(45)
    41
    """

    def __init__(self, firstDiff=None):
        self.values = [None, None]
        self.firstDiff = firstDiff
        self.first = True

    def update(self, value):
        self.values[0] = self.values[1]
        self.values[1] = value

        if self.first:
            self.first = False
            return self.firstDiff
        else:
            return self.values[1] - self.values[0]


class osum():
    """
    Returns the sum of all values that were added ("online sum").

    The starting value of the sum is specified by `start`.

    >>> s = osum()
    >>> s.update(3)
    3
    >>> s.update(7)
    10
    >>> s.update(4)
    14
    >>> s.update(45)
    59
    """

    def __init__(self, start=0):
        self.sum = start

    def update(self, value=1):
        self.sum = self.sum + value
        return self.sum


def median(x):
    """
    Returns the median of the elements of the iterable `x`.

    If the number of elements in `x` is even, the arithmetic mean of the upper
    and lower median values is returned.

    >>> median([3, 7, 4])
    4

    >>> median([3, 7, 4, 45])
    5.5
    """

    s = sorted(x)
    N = len(s)
    if (N % 2) == 1:
        return s[(N - 1) // 2]
    else:
        M = N // 2
        return 0.5 * (s[M - 1] + s[M])


class omedian():
    """
    Returns the median of the last `nLast` values that were added ("online
    median").

    >>> m = omedian(nLast=3)
    >>> m.update(3)
    3
    >>> m.update(7)
    5.0
    >>> m.update(4)
    4
    >>> m.update(45)
    7
    >>> m.update(2)
    4
    >>> m.update(3)
    3
    """

    def __init__(self, nLast=10):
        self.values = collections.deque()
        self.nLast = nLast

    def update(self, value):
        self.values.append(value)
        if len(self.values) > self.nLast:
            self.values.popleft()
        return median(self.values)


def sclip(x, lower=None, upper=None):
    """
    Clips the scalar value `x` to the interval [`lower`, `upper`].

    Each of `lower` and `upper` can be `None`, meaning no clipping.
    The returned result has the same type as the input `x`.

    >>> sclip(123.456, 0, 100)
    100.0
    """

    xType = type(x)
    c = x
    if lower is not None:
        c = xType(max(lower, c))
    if upper is not None:
        c = xType(min(upper, c))
    return c


def tinterval(x, lowerOld, upperOld, lowerNew, upperNew):
    """
    Transform the scalar `x` from the interval [`lowerOld`, `upperOld`] to the
    interval [`lowerNew`, `upperNew`].

    >>> tinterval(0.5, 0.0, 1.0, 1.0, 512.0)
    256.5
    """

    return (x - lowerOld) / (upperOld - lowerOld) * (upperNew - lowerNew) + lowerNew


##
## imports
##


def timport(name):
    """
    Try to import and return the module named `name`, and return `None` on
    failure.
    """

    try:
        return importlib.import_module(name)
    except ImportError:
        return None


##
## development
##


def out(*names):
    """
    Prints the values of the variables specified by `*names`.

    >>> x = 123
    >>> abcdef = 'four'
    >>> out('x', 'abcdef')
    x .... = 123
    abcdef = 'four'

    .. warning:: Only use for debugging!
    """

    # resolve variables to get the values
    values = tuple(resolve(name) for name in names)

    # formatted output
    maxLen = max(len(name) for name in names)
    for (name, value) in zip(names, values):
        print(("{name:.<" + str(maxLen) + "} = {value}").format(name=name if len(name) == maxLen else name + " ", value=repr(value)))


def resolve(name):
    """
    Resolves the variable `name` and returns its value.

    >>> x = 123
    >>> resolve('x')
    123

    .. warning:: The lookup process is NOT identical to Python's builtin one.
                 Only use for debugging!
    """

    frame = inspect.currentframe().f_back
    while frame is not None:
        frameVars = frame.f_locals.items()
        for (varName, varValue) in frameVars:
            if varName == name:
                return varValue
        frame = frame.f_back
    raise RuntimeError("Can not resolve variable name '{name}'".format(name=name))


class Timer():
    """
    Context manager to measure the time between entering and exiting.

    After exiting the `with` block, the elapsed time in seconds can be
    obtained by calling the `Timer` instance object.
    """

    def __enter__(self):
        self.diff = None
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.diff = max(0, self.end - self.start)

    def __call__(self):
        return self.diff


def _pdeco(callerName, fName, message):
    """
    Formats and prints a message, designed to be used by decorator functions
    such as :func:`dh.utils.pentex`, :func:`dh.utils.pargs`, etc.
    """

    print(
        "==> @{callerName}({fName}){spaces}  --  {message}".format(
            callerName=callerName,
            spaces=" " * max(0, 8 - len(callerName)),
            fName=fName,
            message=message
        )
    )


def pentex(f):
    """
    Decorator which prints a message when entering and exiting `f`.

    >>> @pentex
    ... def f(x): return x**2
    >>> res = f(2)
    ==> @pentex(f)    --  enter
    ==> @pentex(f)    --  exit
    """

    @functools.wraps(f)
    def g(*args, **kwargs):
        _pdeco("pentex", f.__name__, "enter")
        ret = f(*args, **kwargs)
        _pdeco("pentex", f.__name__, "exit")
        return ret

    return g


def ptdiff(f):
    """
    Decorator which prints the time difference between entering and exiting
    `f`.
    """

    @functools.wraps(f)
    def g(*args, **kwargs):
        t0 = time.time()
        ret = f(*args, **kwargs)
        t1 = time.time()
        _pdeco("ptdiff", f.__name__, "{dt} seconds".format(
            dt=around(max(0, t1 - t0), 3)
        ))
        return ret

    return g


def pargs(f):
    """
    Decorator which prints the arguments supplied to `f`.

    >>> @pargs
    ... def f(x, y): return x * y
    >>> res = f(2, y=3)
    ==> @pargs(f)     --  (2, y=3)

    .. todo:: truncate each argument value individually (otherwise an image
              array as first argument masks all other arguments)
    """

    @functools.wraps(f)
    def g(*args, **kwargs):
        _pdeco("pargs", f.__name__, "({argstr})".format(
            argstr=tstr(fargs(*args, **kwargs), 120, "<... truncated>"),
        ))
        return f(*args, **kwargs)

    return g


def parghash(f):
    """
    Decorator which prints the hash value (using :func:`dh.utils.ohash`) of the
    arguments supplied to `f`.

    >>> @parghash
    ... def f(x, y): return x * y
    >>> res = f(2, y=3)
    ==> @parghash(f)  --  5cd54cfc
    """

    @functools.wraps(f)
    def g(*args, **kwargs):
        _pdeco("parghash", f.__name__, "{arghash}".format(
            arghash=ohash((args, kwargs), "hex", 4)
        ))
        return f(*args, **kwargs)

    return g


def pret(f):
    """
    Decorator which prints the result returned by `f`.

    >>> @pret
    ... def f(x, y): return {'sum': x + y, 'prod': x * y}
    >>> res = f(2, 3)
    ==> @pret(f)      --  {'prod': 6, 'sum': 5}
    """

    @functools.wraps(f)
    def g(*args, **kwargs):
        ret = f(*args, **kwargs)
        _pdeco("pret", f.__name__, "{retstr}".format(
            retstr=tstr(pprint.pformat(ret), 120, "<... truncated>"),
        ))
        return ret

    return g


def prethash(f):
    """
    Decorator which prints the hash value (using :func:`dh.utils.ohash`) of the
    result returned by `f`.

    >>> @prethash
    ... def f(x, y): return {'sum': x + y, 'prod': x * y}
    >>> res = f(2, 3)
    ==> @prethash(f)  --  3e4601af
    """

    @functools.wraps(f)
    def g(*args, **kwargs):
        ret = f(*args, **kwargs)
        _pdeco("prethash", f.__name__, "{rethash}".format(
            rethash=ohash(ret, "hex", 4)
        ))
        return ret

    return g


def pall(f):
    """
    Decorator which applies the :func:`dh.utils.pentex`,
    :func:`dh.utils.pargs`, :func:`dh.utils.pret`, and :func:`dh.utils.ptdiff`
    decorators on `f`.
    """

    @pentex
    @ptdiff
    @prethash
    @pret
    @pargs
    @parghash
    @functools.wraps(f)
    def g(*args, **kwargs):
        return f(*args, **kwargs)
    return g
