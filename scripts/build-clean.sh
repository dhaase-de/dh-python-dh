#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# clean build output
cd "$PACKAGE_DIR" && ./setup.py clean --all
rm -rf "$PACKAGE_DIR"/*.egg-info/
rm -rf "$PACKAGE_DIR"/dist/

# clean documentation
cd "$DOC_DIR" && make clean
rm -f "$DOC_DIR"/source/dh*.rst
rm -f "$DOC_DIR"/source/modules.rst
rm -f "$DOC_DIR"/source/pylint.rst

# clean bytecode
find "$SOURCE_DIR" -path '*/__pycache__/*.pyc' -type f -delete
find "$SOURCE_DIR" -name '__pycache__' -type d -delete
find "$SOURCE_DIR" -name '*.pyc' -type f -delete
