import numpy as np

import dh.utils

def tir(*args):
    values = dh.utils.flatten(*args)
    return tuple(int(round(value)) for value in values)

