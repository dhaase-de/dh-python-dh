#!/usr/bin/python3

import argparse
import cv2
import json
import numpy as np
import re


def imageToColormap(filename):
    print("Loading image '{filename}'...".format(filename=filename))
    I = cv2.imread(filename, cv2.IMREAD_COLOR)

    # check image dimensions
    if (len(I.shape) != 3) or (I.shape[1:] != (256, 3)):
        raise RuntimeError("Image has shape '{shape}', but must have (>=1, 256, 3)".format(I.shape))

    # create colormap dict (::-1 reverses the channels, as cv2 uses BGR instead of RGB mode)
    c = {value: I[0, value, ::-1].tolist() for value in range(256)}

    # save colormap dict as JSON
    filenameOut = re.sub("\\.[^.]*$", ".json", filename)
    print("Saving colormap dict to '{filenameOut}'...".format(filenameOut=filenameOut))
    with open(filenameOut, "w") as f:
        json.dump(c, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts a colorized gray slope image to a colormap in JSON format which can be loaded by dh.image.colormap")
    parser.add_argument("filename", nargs="+", help="filename of the input image file (this must be the colorized version of the 8 bit gray scale value slope)")
    args = parser.parse_args()
    for filename in args.filename:
        imageToColormap(filename)
