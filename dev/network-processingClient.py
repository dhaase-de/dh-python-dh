#!/usr/bin/python3

import time

import dh.data
import dh.image
import dh.network
import dh.utils


###
#%% main
###


def main():
    C = dh.network.DataProcessingClient("localhost")

    # input
    I = dh.data.lena()
    params = {"gamma": 0.5}
    dh.image.pinfo(I)

    # result
    t0 = time.time()
    J = C.process(I, params)
    t1 = time.time()

    # show result
    print("Received result after {} ms".format(dh.utils.around((t1 - t0) * 1000.0)))
    dh.image.show(dh.image.stack([I, J]), wait=0)


if __name__ == "__main__":
    main()
