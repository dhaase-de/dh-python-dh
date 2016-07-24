#!/usr/bin/python3

import math
import time

import dh.utils


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
    main()
