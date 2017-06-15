#!/usr/bin/python3

import dh.data
import dh.image


def main():
    L = dh.data.lena()
    P = dh.data.pal()
    B = dh.data.background()

    dh.image.show(L, wait=0, closeWindow=True)
    dh.image.show([L, P, B], wait=0, closeWindow=True)
    dh.image.show([[L, P, B]], wait=0, closeWindow=True)


if __name__ == "__main__":
    main()
