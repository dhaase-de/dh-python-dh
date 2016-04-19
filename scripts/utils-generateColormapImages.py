#!/usr/bin/python3

import argparse
import cv2
import numpy as np
import os.path


def generateColormapsCv2(S):
    names = {
        "autumn",
        "bone",
        "cool",
        "hot",
        "hsv",
        "jet",
        "ocean",
        "pink",
        "rainbow",
        "spring",
        "summer",
        "winter",
    }
    colormaps = {}
    for name in names:
        c = getattr(cv2, "COLORMAP_" + name.upper())
        colormaps[name.lower()] = cv2.applyColorMap(S, c)[:,:,::-1]
    return colormaps


def generateColormapsMatplotlib(S):
    import matplotlib.cm
    names = (
        "Accent",
        "Blues",
        "BrBG",
        "BuGn",
        "BuPu",
        "Dark2",
        "GnBu",
        "Greens",
        "Greys",
        "OrRd",
        "Oranges",
        "PRGn",
        "Paired",
        "Pastel1",
        "Pastel2",
        "PiYG",
        "PuBu",
        "PuBuGn",
        "PuOr",
        "PuRd",
        "Purples",
        "RdBu",
        "RdGy",
        "RdPu",
        "RdYlBu",
        "RdYlGn",
        "Reds",
        "Set1",
        "Set2",
        "Set3",
        "Spectral",
        "YlGn",
        "YlGnBu",
        "YlOrBr",
        "YlOrRd",
        "autumn",
        "binary",
        "bone",
        "cool",
        "copper",
        "flag",
        "gist_earth",
        "gist_gray",
        "gist_heat",
        "gist_ncar",
        "gist_rainbow",
        "gist_stern",
        "gist_yarg",
        "gray",
        "hot",
        "hsv",
        "jet",
        "pink",
        "prism",
        "spectral",
        "spring",
        "summer",
        "winter",
    )
    colormaps = {}
    for name in names:
        c = getattr(matplotlib.cm, name)
        colormaps[name.lower()] = np.round(255.0 * c(S)[:,:,:3]).astype("uint8")
    return colormaps


def generateColormaps(targetDir):
    # load gray scale slope image (1x256 pixels)
    S = cv2.imread(os.path.join(os.path.dirname(__file__), "utils-generateColormapImages-graySlope.png"), cv2.IMREAD_GRAYSCALE)

    colormaps = {}
    colormaps.update(generateColormapsCv2(S))
    colormaps.update(generateColormapsMatplotlib(S))

    for (name, C) in colormaps.items():
        filenameOut = "{}.png".format(name.lower())
        print("Saving colormap image '{}'".format(filenameOut))
        cv2.imwrite(os.path.join(targetDir, filenameOut), C[:,:,::-1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Applies various colormaps on the standard gray scale slope image and saves the colorized images (which can then be converted to JSON via 'utils-convertColormapImagesToJson.py')")
    parser.add_argument("targetDir", help="directory where the resulting image files are saved to")
    args = parser.parse_args()
    generateColormaps(**vars(args))
