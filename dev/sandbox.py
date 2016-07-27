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


def main():
    rows = []
    for nRow, row in enumerate(dh.utils.pbar(range(1250), unit="rows")):
        rows.append({
            "X": 9.37 + nRow * math.pi,
            "Y": "hallo",
        })
        time.sleep(0.1)
    dh.utils.ptable(rows)


if __name__ == "__main__":
    timer()
