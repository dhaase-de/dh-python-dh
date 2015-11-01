#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
DOC_DIR="$SCRIPT_DIR"/doc

# clean build output
"$SCRIPT_DIR"/setup.py clean --all

# clean documentation
cd "$DOC_DIR" && make clean
rm -f "$DOC_DIR"/source/dh*.rst
rm -f "$DOC_DIR"/source/modules.rst
rm -f "$DOC_DIR"/source/pylint.rst

# clean bytecode
find "$SCRIPT_DIR" -path '*/__pycache__/*.pyc' -type f -delete
find "$SCRIPT_DIR" -name '__pycache__' -type d -delete
find "$SCRIPT_DIR" -name '*.pyc' -type f -delete
