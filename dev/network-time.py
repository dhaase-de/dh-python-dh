#!/usr/bin/python3

import io
import time
import zlib

import numpy as np

import dh.data
import dh.utils


###
#%% main
###


def serializeJson(X):
    return dh.utils.ejson.dumps(X).encode("ascii")


def serializeJsonGzip(X):
    return zlib.compress(dh.utils.ejson.dumps(X).encode("ascii"), 6)


def serializeNumpy(X):
    b = io.BytesIO()
    np.save(b, X)
    return b.getvalue()


def serializeNumpyStrict(X):
    b = io.BytesIO()
    np.save(b, X, allow_pickle=False, fix_imports=False)
    return b.getvalue()


def main():
    X = dh.data.lena()

    ts = []
    ls = []
    fs = (serializeJson, serializeJsonGzip, serializeNumpy, serializeNumpyStrict)
    for f in fs:
        dts = []
        for nLoop in range(10):
            t0 = time.time()
            b = f(X)
            assert isinstance(b, bytes)
            dts.append(time.time() - t0)
        ts.append(dh.utils.mean(dts))
        ls.append(len(b))

    dh.utils.ptable(
        [[f.__name__, t * 1000.0, l / 1024.0] for (f, t, l) in zip(fs, ts, ls)],
        headers=["f", "time [ms]", "KiB"]
    )


if __name__ == "__main__":
    main()

