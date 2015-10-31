#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get absolute path of this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# clean build output
"$SCRIPT_DIR"/setup.py clean --all

# clean bytecode
find "$SCRIPT_DIR" -path '*/__pycache__/*.pyc' -type f -delete
find "$SCRIPT_DIR" -name '__pycache__' -type d -delete
find "$SCRIPT_DIR" -name '*.pyc' -type f -delete

