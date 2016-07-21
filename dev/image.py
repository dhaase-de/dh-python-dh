#!/usr/bin/python3

import dh.data
import dh.image


def main():
    I1 = dh.data.lena()
    I2 = dh.image.convert(dh.data.M(300, 200).astype("uint16"), "uint8")
    I3 = dh.data.grid([350, 500])
    I4 = dh.data.pal()
    I5 = dh.data.grid([200, 200])

    S = dh.image.stack([[I1, I2], [I3, I4], [I5]])
    dh.image.imshow(S)


if __name__ == "__main__":
    main()
