#!/usr/bin/python3

import math
import time

import dh.utils


def timer():
    with dh.utils.Timer() as t:
        print(t)
        time.sleep(0.123)
        t.split()
        time.sleep(0.5)
        t.split("yet another")
        time.sleep(0.0001)
        t.split()
        time.sleep(0.2)
    print(t)


def avdict():
    a = dh.utils.avdict(x = 3, y = 2)
    print(a.y)


if __name__ == "__main__":
    avdict()
