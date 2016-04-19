#!/usr/bin/python3

import dh.data
import dh.image


def main():
    L = dh.image.asgray(dh.data.lena())
    C = dh.image.colorize(L, "magma", False)
    dh.image.imshow(C)


if __name__ == "__main__":
    main()
