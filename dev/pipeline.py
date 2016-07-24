#!/usr/bin/python3


import dh.data
import dh.image
import dh.image.pipeline


def main():
    M = dh.data.M().astype("uint8")
    L = dh.data.lena()
    P = dh.data.pal()
    G = dh.data.grid(w=3)

    v = dh.image.pipeline.Viewer()
    v.add(M)
    v.add(P)
    v.add(G)
    v.add(L)

    v.show()


if __name__ == "__main__":
    main()
