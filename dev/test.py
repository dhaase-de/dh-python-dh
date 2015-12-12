#!/usr/bin/python3

import os
import subprocess


##
## tests
##


def test_image():
    import dh.data
    import dh.image
    import dh.image.viewer

    M = dh.data.M().astype("uint8")
    L = dh.data.lena()
    P = dh.data.pal()
    G = dh.data.grid(w=3)

    v = dh.image.viewer.Viewer()
    v.add(M)
    v.add(P)
    v.add(G)
    v.add(L)

    v.show()


##
## main
##


def install():
    print("Installing package 'dh'...")
    workingDir = os.getcwd()
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(scriptDir + "/..")
    subprocess.call(
        ["./scripts/build-install.sh"],
        stdout=open(os.devnull, 'wb')
    )
    os.chdir(workingDir)
    print("done")
    print("-" * 26)


if __name__ == "__main__":
    install()
    test_image()
    #test_pipeline()
