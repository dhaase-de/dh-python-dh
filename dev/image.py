#!/usr/bin/python3

import numpy as np

import dh.data
import dh.image


def stack():
    L = dh.data.lena()
    M = dh.image.convert(dh.data.M(300, 200).astype("uint16"), "uint8")
    G1 = dh.data.grid([350, 500])
    G2 = dh.data.grid([200, 200])
    P = dh.data.pal()

    S = dh.image.stack([[L, M], [G1, G2], [P]], padding=0)
    print(S.shape)
    dh.image.imshow(S, scale=None, wait=0)


def astack():
    I1 = dh.data.lena()
    I2 = dh.data.grid([350, 500])
    I3 = dh.data.pal()
    I4 = dh.data.grid([200, 200])

    #S = dh.image.astack([I1, I2, I3, I4], padding=32)
    S = dh.image.astack([I1] * 9, padding=32, aspect=1.77)
    dh.image.imshow(S, scale=0.3, wait=10)


def clip():
    I = dh.data.lena()
    dh.image.pinfo(I)
    I = dh.image.clip(I, -10.0, 127.7)
    dh.image.pinfo(I)
    dh.image.imshow(I, wait = 50)


def convert():
    A = np.array([[-12]], dtype = "float")
    print(dh.image.convert(A, "uint8"))


def imdiff():
    A = np.array([0, 1, 2, 3, 4, 255], dtype="uint8")
    B = np.array([1, 0, 2, 255, 2, 2], dtype="uint8")
    dh.image.pinfo(dh.image.imdiff(A, B))


def dog():
    I = dh.image.asgray(dh.data.lena())
    D = dh.image.dog(I, 0.25, 3.0, False)
    dh.image.imshow(D, wait = 20, scale = 0.5, normalize = "percentile", q = 1.0)


def resize():
    I = dh.data.M().astype("uint8") * 20
    R = dh.image.resize(I, 100.0)
    dh.image.imshow(R, scale=1.0, wait=1000)


def text():
    I = dh.data.lena()
    I[I.shape[0] // 2, :, :] = 255
    I[:, I.shape[1] // 2, :] = 255
    I = dh.image.text(I, "Error quantile:", position=(0.5, 0.5), anchor="cc", padding=1.5)
    dh.image.imshow(I, wait=10, scale=1.0)


def cdemo():
    I = dh.data.lena()
    I = dh.image.asgray(I)
    dh.image.cdemo()


def show():
    I = dh.data.lena()
    I = dh.image.asgray(I)
    dh.image.show(I >= 127, wait=0)
    dh.image.show(I, wait=0, colormap="jet")
    dh.image.show(I, wait=0)


if __name__ == "__main__":
    show()
