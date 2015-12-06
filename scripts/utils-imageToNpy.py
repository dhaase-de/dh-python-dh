#!/usr/bin/python3

import argparse
import numpy as np
import os
import re
import skimage.io


def imageToNpy(filename, compress):
    # load image
    print("Loading image '{filename}'...".format(filename=filename))
    X = skimage.io.imread(filename)
    print("Shape: {shape}, dtype: {dtype}".format(shape=X.shape, dtype=X.dtype))

    # save numpy array
    filenameOut = re.sub("\\.[^.]*$", ".npz", filename)
    print("Saving NumPy image '{filenameOut}'...".format(filenameOut=filenameOut))
    if compress:
        np.savez_compressed(filenameOut, X)
    else:
        np.savez(filenameOut, X)

    # print new file size
    filesize = os.stat(filenameOut).st_size
    print("NumPy file size is {}kB".format(int(round(filesize / 1024.0))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert image files to the NumPy format (.npy, .npz)")
    parser.add_argument("filename", help="filename of the input image file")
    parser.add_argument("-u --uncompressed", dest="compress", action="store_const", const=False, default=True, help="turn off NumPy compression for the output file")
    args = parser.parse_args()
    imageToNpy(**vars(args))
