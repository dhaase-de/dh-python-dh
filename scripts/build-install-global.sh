#!/bin/bash

# robust bash scripting
set -o errexit
set -o nounset

# get important dirs of this Python package (absolute paths)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR"/setenv.sh

# update version in file "dh/VERSION.txt"
"$SCRIPT_DIR"/version-setFromGit.sh

# run local installation
cd "$PACKAGE_DIR" && python3 setup.py install
