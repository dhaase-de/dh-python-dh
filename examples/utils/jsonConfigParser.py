#!/usr/bin/python3

import dh.utils


def main():
    C = dh.utils.JsonConfigParser()
    C.add_section("Test")
    C.set("Test", "i", 1)
    C.set("Test", "b", True)
    C.set("Test", "s", "A string!")
    C.set("Test", "f", -1e23)
    C.set("Test", "tuple", (1, -2))
    C.set("Test", "dict", {"a": 123, "B": 12.34})
    with open("test.conf", "w") as f:
        C.write(f)

    C = dh.utils.JsonConfigParser()
    C.read("test.conf")
    value = C["Test"]["tuple"]
    print(type(value))
    print(value)


if __name__ == "__main__":
    main()
