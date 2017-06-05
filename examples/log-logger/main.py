#!/usr/bin/python3

import dh.log


###
#%% main
###


def main():
    L = dh.log.Logger(minLevel=dh.log.Logger.LEVEL_INFO, colored=True, inspect=False)
    L.debug("This is a debug message")
    L.info("This is an info message")
    L.warning("This is a warning message")
    L.error("This is an error message")
    L.critical("This is a critical message")


if __name__ == "__main__":
    main()

