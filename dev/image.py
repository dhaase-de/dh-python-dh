#!/usr/bin/python3

import dh.data
import dh.image


def stack():
    I1 = dh.data.lena()
    I2 = dh.image.convert(dh.data.M(300, 200).astype("uint16"), "uint8")
    I3 = dh.data.grid([350, 500])
    I4 = dh.data.pal()
    I5 = dh.data.grid([200, 200])

    S = dh.image.stack([[I1, I2], [I3, I4], [I5]])
    dh.image.imshow(S)


def clip():
    I = dh.data.lena()
    dh.image.pinfo(I)
    I = dh.image.clip(I, -10.0, 127.7)
    dh.image.pinfo(I)
    dh.image.imshow(I, wait = 50)


if __name__ == "__main__":
    clip()
