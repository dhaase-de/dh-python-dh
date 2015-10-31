#!/usr/bin/python3

import os.path
import time
import pickle

def dictToList(d):
    if type(d) != type({}):
        return d

    l = []
    for (key, value) in d.items():
        l.append([dictToList(key), dictToList(value)])
    
    return l

def cache(fun):
    cacheFilename = __file__ + ".cache.pkl"

    def decorated(*args, **kwargs):
        key = {
            "fun": fun.__name__,
            "args": args,
            "kwargs": kwargs,
        }
        key = str(key)
        print(key)
        
        if os.path.exists(cacheFilename):
            with open(cacheFilename, "rb") as f:  
                cache = pickle.load(f)
        else:
            cache = {}
        
        if key in cache:
            print("USE CACHE")
            return cache[key]
        else:
            print("NO CACHE")
            value = fun(*args, **kwargs)
            cache[key] = value
            with open(cacheFilename, "wb") as f:   
                pickle.dump(cache, f)
            return value

    return decorated

@cache
def k(x):
    time.sleep(0.5)
    return x**2

def runTest():
    k(2)
    k(3)
    k(4)
    k(x = 2)

if __name__ == "__main__":
    #print(__file__)
    runTest()

