#!/usr/bin/python3

import os
import subprocess
import time

def test():
    import dh.utils
    
    @dh.utils.pall
    def bla(x, y, *args, **kwargs):
        time.sleep(0.345678)
        return [x["a"] + y["b"], None]
        
    bla({"a": 1}, {"b": 2}, n=1, m=2)


def install():
    print("Installing package 'dh'...")
    workingDir = os.getcwd()
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(scriptDir + "/..")
    subprocess.call(["./install.sh"], stdout = open(os.devnull, 'wb'))
    os.chdir(workingDir)
    print("done")
    print("-" * 26)

if __name__ == "__main__":
    install()
    test()

