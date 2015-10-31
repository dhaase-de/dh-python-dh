#!/usr/bin/python3

import datetime
import time

##
## tictoc
##

tictocDepth = 0
def tictoc(f):
    # settings
    

    # helper functions
    def formatTimeAbs(t):
        return t.strftime("%Y-%m-%d %H:%M:%S.%f")
        
    def formatTimeDiff(t0, t1):
        return datetime.timedelta.total_seconds(t1 - t0)
    
    # generate decorated function
    def decorated(*args, **kwargs):
        global tictocDepth

        # tic
        tic = datetime.datetime.now()
        tictocDepth += 1
        print("[{time}]  {indent}tic  name=\"{name}\"".format(time = formatTimeAbs(tic), indent = ".." * (tictocDepth - 1), name = f.__name__))
        
        # call actual function
        res = f(*args, **kwargs)
        
        # toc
        toc = datetime.datetime.now()
        print("[{time}]  {indent}toc  name=\"{name}\" total={diff}".format(time = formatTimeAbs(toc), indent = ".." * (tictocDepth - 1), diff = formatTimeDiff(tic, toc), name = f.__name__))
        tictocDepth -= 1
        
        return res
    
    return decorated

def tictocTest():
    @tictoc
    def g(x):
        time.sleep(0.1)
        return 1 - x

    @tictoc
    def f(x):
        return g(x**2)

    f(2)
    
##
## main
##
    
if __name__ == "__main__":
    tictocTest()

