#!/usr/bin/python3

import os.path

import dh.log


###
#%% main
###


def main():
    for fmt in ("plain", "minimal", "bullet", "short", "long"):
        print("=" * 20)
        L = dh.log.Logger(
            formatter=(fmt, "long"),
            filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out.log"),
            minLevel=(dh.log.Logger.LEVEL_DEBUG, dh.log.Logger.LEVEL_INFO),
            color=True,
        )
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

