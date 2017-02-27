#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# find nosetests binary
NOSETESTS_BIN=$(which nosetests3 || which nosetests)

# run tests
cd "$PACKAGE_DIR" && "$NOSETESTS_BIN" dh --with-doctest --verbosity=3
