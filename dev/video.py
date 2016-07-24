#!/usr/bin/python3

import cv2

import dh.data
import dh.image


def main():
    I = dh.data.lena()
    print(I.shape)
    #()
    v = cv2.VideoWriter()
    res = v.open(
        filename="/home/dh/tmp/video.mpg",
        fourcc=cv2.VideoWriter_fourcc("M", "J", "P", "G"),
        fps=24.0,
        frameSize=I.shape[:2][::-1],
        isColor=True,
    )
    print(res)

    for i in range(24):
        print(i)
        J = dh.image.shift(I, dx = i)
        v.write(J)
    v.release()

if __name__ == "__main__":
    main()
