#!/usr/bin/python3

import dh.log


###
#%% main
###


def main():
    for fmt in ("long", "short"):
        L = dh.log.Logger(fmt, "./")
        L.debug("This is a debug message")
        L.info("This is an info message")
        L.success("This is a success message")
        L.warning("This is a multi-line\nwarning message")
        L.error("This is an error message")
        L.critical("This is a critical message")
        L.info("This is an info message")
        L.pprint({"a": [1, 2, 3], "b": None, 3: 123456, (12, 34): 56, "asdfg": "TEST TEST TEST TEST TEST TEST TEST TEST"}, "x")

        m = L.pending("Setting up foo-bar...")
        m.ok()
        m.failed("Error in step 7")


if __name__ == "__main__":
    main()

