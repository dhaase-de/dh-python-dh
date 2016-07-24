#!/usr/bin/python3

import importlib


def f():
    import cv2
    g()


def g():
    print(cv2.__version__)


def main():
    f()


if __name__ == "__main__":
    main()
