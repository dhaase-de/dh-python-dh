#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# run global installation
cd "$PACKAGE_DIR" && python3 setup.py install
