#!/usr/bin/env python3

import time

import dh.data
import dh.image
import dh.network
import dh.utils


###
#%% main
###


def main():
    C = dh.network.ImageProcessingClient2("localhost")

    # input
    I = dh.data.lena()
    params = {"gamma": 0.5}
    print("Input:")
    dh.image.pinfo(I)

    # result
    t0 = time.time()
    (J, info) = C.process(I, params)
    t1 = time.time()

    # show result
    print("Output:")
    dh.image.pinfo(J)
    print("Info:")
    print(info)
    print("Received result after {} ms".format(dh.utils.around((t1 - t0) * 1000.0)))
    dh.image.show(dh.image.stack([I, J]), wait=0, closeWindow=True)


if __name__ == "__main__":
    main()
