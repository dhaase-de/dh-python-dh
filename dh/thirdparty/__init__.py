##
## wrappers for "atomicwrites" module
##

import dh.thirdparty.atomicwrites

def atomic_write_open(path):
    return dh.thirdparty.atomicwrites.atomic_write(path, overwrite = True)

