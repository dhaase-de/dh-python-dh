#!/usr/bin/python3

import os
import subprocess

def testTir():
    import dh.sci
    
    def t(*args):
        print(dh.sci.tir(args))
        
    t([1.2, 7.8])
    t(1.2, 7.8)
    t([1.2, 7.8], 3.4)
    t([1.2, 7.8, [3.4]])
    t(1.2, 7.8, 3.4)

def testFlatten():
    import dh.utils
    def f(*args):
        print(list(dh.utils.flatten(args)))
        
    f([1, 2, [3, 4], [5, [6, [7]]], [8, 9], 10], 11, [12, 13], [14, [15, [16]]])

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
    #testFlatten()
    testTir()

