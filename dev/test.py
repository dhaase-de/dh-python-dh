#!/usr/bin/python3

import os
import subprocess
import time

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

